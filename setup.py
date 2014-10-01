import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "ISStreamer",
	version = "0.0.2",
	author = "David Sulpy, Initial State Technologies",
	author_email = "david@initialstate.com",
	description = ("A python module and commandline tool to simplify the process of getting log data to Initial State's platform"),
	license = "MIT",
	keywords = "logger logstream initial state",
	url = "https://www.initialstate.com",
	packages=['ISStreamer'],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Topic :: Utilities",
		"License :: OSI Approved :: MIT License"
	]
)