Python Data Streamer
===============

[![Join the chat at https://gitter.im/InitialState/python_appender](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/InitialState/python_appender?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) 

[![Build Status](https://travis-ci.org/initialstate/python_appender.svg?branch=master)](https://travis-ci.org/initialstate/python_appender)

This is a Python module currently built for python >= 2.7

## Installation

### Using the automated script

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


### Using Package Management
The package is hosted in PyPI under the package name [ISStreamer](https://pypi.python.org/pypi/ISStreamer).

#### If you don't have `pip`:

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

#### I've got `pip` what next?:


```
$ sudo pip install ISStreamer
```

> This command installs the ISStreamer module
	

## Basic Usage

After getting the ISStreamer module, usage is really simple. With the following example, you can do most of what you need, and you **don't need to read further**! However


```python
from ISStreamer.Streamer import Streamer

# create or append to a Streamer instance
streamer = Streamer(bucket_name="Some Bucket Name", bucket_key="bucket_key", access_key="YourAccessKey")

# send some data
streamer.log("test", "hi")
streamer.log("temperature", 32)

# flush data (force the buffer to empty and send)
streamer.flush()

# close the stream
streamer.close()
```


## Advanced Usage, Troubleshooting, and Concepts


### Concepts

- #### Buckets

	In order to keep your event streams and visualizations contextually appropriate, we have implemented a concept called `buckets`. A new bucket is automatically created when the Streamer is constructed, however, if you want to append to an existing bucket, or use a key that is more memorable than the uuid that will otherwise be used, you can use the optional `bucket_key` constructor parameter. If a Streamer is constructed with a `bucket_key` that already exists, then any data sent in that Stream will append to the existing bucket.

	> NOTE: `bucket_key`'s uniqueness is scoped to a specific `access_key`.

- #### Event Stream

	An event stream is a key with an associated set of values with timestamps. These individual events are created every time the `Strmeaer.log` method is called. If an `event_key` is the same for different pieces of data, those pieces of data are represented together in an event stream. This is more of an Initial State concept than a Python Streamer specific concept.

	> Legacy Note: Event Streams use to be called Signals.

### Most Used Methods

- #### `Streamer.log(key, value[, epoch])`
	This is the core method and api for the event streamer. This is an asyncronous method that pushes your data to a queue that handles sending it off to Initial State's servers. You don't have to worry about anything but calling the method where you want! For the sake of clarity (for those new to python or programming) the `Streamer` would be replaced with the variable reference to a `Streamer` instance.
	
	The `log` method expects two parameters, `key` and `value`:
	- `key` is a string that represents the source of the `value` and is limited to 250 characters
	- `value` is either a string, boolean, or number and it represents a value at the time of the method call.
	- `epoch` is an optional parameter to override the epoch timestamp, recommended for advanced uses.

- #### `Streamer.log_object(obj[, key_prefix[, epoch]])`
	This is an enhanced method to abstract having to write a bunch of log statements to stream all of the values of an object with multiple data points at a specific time.

	The `log_object` method expects one parameter, `obj`:
	- `obj` is either a list, dict, or simple object with attributes.
		- If `obj` is a list, it will use the key name `list_n` unless the optional `key_prefix` is supplied, then it will use `key_prefix_n` where `n` - in both cases - is an index.
		- If `obj` is a dict, it will use the key name `dict_key` where unless the optional `key_prefix` is supplied, then it will use `key_prefix_key` where `key` - in both cases - is the key of the dictionary value.
		- If `obj` is a simple object, it will iterate over the objects attributes and produce values for keys with the name of the key as `obj_attr` unless the `key_prefix` is supplied, then it will use `key_prefix_attr`. In all cases, `attr` is the attribute name.
	- `key_prefix` is an optional string that, when supplied, overrrides the default key prefixes.
	- `epoch` is an optional number that represents the current time in epoch format.

	[Here is a working example](/example_app/example_compute_metrics.py).

	> NOTE: log_object will log multiple keys and values, but will override the epoch timestamp of each value so that there is no cpu or iteration skew in the timestamp reported for when those values were logged and streamed.

- #### `Streamer.close()`
	This method ensures that the log buffer is flushed and should be called when a program is exiting. It is also called during the `__del__` magic method of the `Streamer` by python, but it is a best practice to explicitly call it at the end of a program to ensure it is executed.

### Advanced Use

- #### Manual `Streamer.flush()`
	You can manually flush on your own accord by calling `Streamer.flush()`. This will ensure that anything that has been queued or buffered locally  will get sent to Initial State's servers asap.
	
- #### Changing buffer size
	You can override the default event buffer size (the count of events) by passing the optional `buffer_size` parameter into the Streamer constructor. Here is an example:

	```python
	streamer = Streamer(bucket_name="Hi!", access_key="YourAccessKey", buffer_size=200)
	```

	In this example, the `buffer_size` is being increased to 200 from the default, 10. The decision to override this value should be based on how many log statements you make in a loop before sleeping. You can typically play around with this number to help tune the performance of the Streame. Additionally, a higher buffer_size may help if getting throttled by the api.

	Another great example of overriding the buffer_size would be to increase to a large value and use the `Streamer.flush()` method at the end of each iteration to effectively have a dynamic buffer size. Here is an example:

	```python
	...

	streamer = Streamer(bucket_name="Dynamic Buffer", access_key="YourAccessKey", buffer_size=200)

	counter = 0
	while 1:
		streamer.log("loop_counter", counter)

		some_dict = {
			"a": 1,
			"b": 2,
			"c": 3
		}
		streamer.log_object(some_dict, key_prefix="some_dict")

		dynamic_list = SomeOtherModule.PracticalClass.get_stuff()
		
		# We don't know how many items will be in dynamic_list, so we just
		# log the list to get them all. However, since we don't know how many
		# there will be, we don't know the optimal buffer size, so we set the
		# buffer to a high value and flush at the end of the iteration
		streamer.log_object(dynamic_list)

		# Here we will flush the log buffer to insure that there isn't a delay
		# in sending the logs that we've created previous to this point while
		# waiting for the sleep to finish
		streamer.flush()

		# increment counter
		counter += 1

		# sleep for 10 seconds
		time.sleep(10)

	...
	```

- #### Overriding the timestamp
	Some have asked for the ability to override the timestamp. Currently, the timestamp is automatically associated with data by retrieving the most accurate timestamp possible from the device as soon as a `log` or `log_object` method is called. However, you can override this by doing the following:

	```python

	time = time.time()

	streamer.log("siganl", 5, epoch=time)

	```

	For a full example checkout [this](/example_app/time_override_example.py)


- #### Creating a new bucket
	When you construct a `Streamer` the constructor expects a name or a key that it will use to ensure there is a bucket that it will use as the context for `Streamer.log(key, value)`. Buckets are either created or consumed based on the unique combination of a `access_key` and a `bucket_key`. If you want to switch which to a new bucket, because say you've started a new session or run, simply call `Streamer.set_bucket(bucket_name='some_bucket_name'[, bucket_key='some_bucket_key'])`. Note that bucket_key is optional, if not provided the module will create a `uuid4` as the `bucket_key`. Here is an example:
	
	```python
	streamer = Streamer(bucket_name="Starting Bucket", access_key="YourAccessKey")
	
	streamer.log("key1", "starting")
	streamer.set_bucket(bucket_name="New Bucket")
	streamer.log("key1", "starting")
	```  

	In this example, you will get a key1=starting in two different buckets: "Starting Bucket" and "New Bucket".


### Troubleshooting

#### Missing Events
If the Streamer cannot ship a set of events during a flush, it will retry a few times before deeming it a failure. If it does fail, it will attempt to save it's payload to a local file. This payload will be in a json format inside a json array. Each array can be individually submitted to Initial State's events api to fill in any missed events.

#### Setting `debug_level`
If you're having issues with your data you might want to try running ISStreamer at a higher debug level:

```python
logger = Streamer(bucket_name="SomeBucketName", access_key="YourAccessKey", debug_level=2)
```

With a `debug_level` at or greater than 2 the streamer will throw exceptions on logging errors. Otherwise, it will assume logging errors are not fundamentally exceptional. It will also display more verbouse logging information.

> If you want to simply see what's being logged in the console, construct the Streamer object with the debug_level equal to 1.
