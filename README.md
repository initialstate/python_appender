Python Data Streamer/Shipper
===============

This is a Python module currently built for python 2.7 to stream data to the Initial State platform.

##Installation
The package is hosted in PyPI under the package name [ISStreamer](https://pypi.python.org/pypi/ISStreamer).

1. (*opional*) If you're on Raspbean or any other Debian based OS and you do not have python-dev tools, you'll need to get it first.
	
	```
	$ sudo apt-get install python-dev
	```

2. (*optional*) Check if you have python setup tools installed:

	```
	$ easy_install --version
	```
	
	if you don't see a version number come back, you should install setuptools:
	
	

3. (*optional*) Check if you have pip installed:

	```
	$ pip --version
	```
	
	if you don't see a version number after running the above command, install pip using easy_install:
	
	```
	$ sudo easy_install pip
	```


4. Install the ISStreamer module (currently it's an Alpha package, so you will need to specify the `--pre` command flag)
	
	```
	$ sudo pip install ISStreamer --pre
	```

##Usage
After getting the ISStreamer module, usage is really simple:


```
from ISStreamer.Streamer import Streamer

var logger = new Streamer(bucket="SomeBucketName", client_key="YourClientKey")

logger.log("signal_test", "hi")
logger.log("temperature", 32)
```