Python Data Streamer
===============

This is a Python module currently built for python >= 2.7

##Installation
###Using the automated script

On a Unix based system: (including Raspberry Pi, Mac OS X, Ubuntu) 

```
\curl -sSL https://get.initialstate.com/python -o - | sudo bash
```

If you don't have `curl` you should get it

```
sudo apt-get install curl
```

```
sudo yum install curl
```


###Using Package Management
The package is hosted in PyPI under the package name [ISStreamer](https://pypi.python.org/pypi/ISStreamer).

####If you don't have `pip`:

1. (*optional*) Check if you have python setup tools installed:

	```
	$ easy_install --version
	```
	
	if you don't see a version number come back, you should install setuptools:
	
	```
	$ sudo apt-get install python-setuptools
	```
	

2. (*optional*) Check if you have pip installed:

	```
	$ pip --version
	```
	
	if you don't see a version number after running the above command, install pip using easy_install:
	
	```
	$ sudo easy_install pip
	```

####I've got `pip` what next?:


```
$ sudo pip install ISStreamer --pre
```

> This command installs the ISStreamer module (currently it's an Alpha package, so you will need to specify the `--pre` command flag)
	

##Basic Usage

After getting the ISStreamer module, usage is really simple. With the following example, you can do most of what you need, and you **don't need to read further**! However


```python
from ISStreamer.Streamer import Streamer

# create a Streamer instance
streamer = Streamer(bucket="SomeBucketName", client_key="YourClientKey")

# log some data
streamer.log("signal_test", "hi")
streamer.log("temperature", 32)

# flush and close the stream
streamer.close()
```


##Advanced Usage, Troubleshooting, and Concepts


###Concepts
- ####Buckets
	In order to keep your logs and visualizations contextually appropriate, we have implemented a concept called `buckets`. The name of a bucket is like the name of a log file. They also behave similarly. If a bucket exists with the same name in your account and you log data to this bucket, you should expect that data to append, just like to an existing log file.
	
- ####`Streamer.log(signal, value[, epoch])`
	This is the core method and api for the log streamer. This is an asyncronous method that pushes your data to a queue that handles sending it off to Initial State's servers. You don't have to worry about anything but calling the method where you want! For the sake of clarity (for those new to python or programming) the variable `logger` in this case can be whatever you assign it to be, it's just the representation of the constructed `Streamer` object.
	
	The `log` method expects two parameters, `signal` and `value`:
	- `signal` is a string that represents the source of the `value`
	- `value` is either a string, boolean, or number and it represents a value at the time of the method call.
	- `epoch` is an optional parameter to override the epoch timestamp, recommended for advanced uses.

- ####`Streamer.log_object(obj[, signal_prefix[, epoch]])`
	This is an enhanced method to abstract having to write a bunch of log statements to log all of the values of an object.

	The `log_object` method expects one parameter, `obj`:
	- `obj` is either a list, dict, or simple object with attributes.
		- If `obj` is a list, it will use the signal name `list_n` unless the optional `signal_prefix` is supplied, then it will use `signal_prefix_n` where `n` - in both cases - is an iterator identifier.
		- If `obj` is a dict, it will use the signal name `dict_key` where unless the optional `signal_prefix` is supplied, then it will use `signal_prefix_key` where `key` - in both cases - is the key of the dictionary value.
		- If `obj` is a simple object, it will iterate over the objects attributes and produce values for signals with the name of the signal as `obj_attr` unless the `signal_prefix` is supplied, then it will use `signal_prefix_attr`. In all cases, `attr` is the attribute name.
	- `signal_prefix` is an optional string that optionally overrrides the default signal prefixes.
	- `epoch` is an optional number that represents the current time in epoch format.

	> NOTE: log_object will log multiple signals and values, but will override the timestamp of all values to ensure the values are relateable and there is no cpu based skew between the values being logged to the buffer.


###Advanced Use
- ####Manual `flush()`
	You can manually flush at your own accord by calling `Streamer.flush()`. This will ensure that anything that has been queued locally  will get sent to Initial State's log processing servers.
	
- ####Creating a new bucket
	When you construct a `Streamer` the constructor expects a name that it will assign to a new bucket that it will use as the context for `Streamer.log(signal, value)`. The bucket is created new every time the `Streamer` is constructed. If you want to switch which to a new bucket, because say you've started a new session or run, simply call `Streamer.new_bucket('some_bucket_name')` here is an example:
	
	```python
	streamer = Streamer(bucket="starting_bucket", client_key="YourClientKey")
	
	streamer.log("signal1", "starting")
	streamer.new_bucket("new_bucket")
	streamer.log("signal1", "starting")
	```  

	In this example, you will get a signal1=starting in two different buckets: "starting_bucket" and "new_bucekt".


###Troubleshooting
####Setting `debug_level`
If you're having issues with your data you might want to try running ISStreamer at a higher debug level:

```python
logger = Streamer(bucket="SomeBucketName", cluent_key="YourClientKey", debug_level=2)
```

With a `debug_level` at or greater than 2 the streamer will throw exceptions on logging errors. Otherwise, it will assume logging errors are not fundamentally exceptional. It will also display more verbouse logging information.

> If you want to simply see what's being logged in the console, construct the Streamer object with the debug_level equal to 1.