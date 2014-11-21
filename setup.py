import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

from distutils.util import convert_path
main_ns = {}
ver_path = convert_path('ISStreamer/version.py')
with open(ver_path) as ver_file:
	exec(ver_file.read(), main_ns)

setup(
	name = "ISStreamer",
	version = main_ns['__version__'],
	
	packages=['ISStreamer'],

	package_dir={
		"ISStreamer": "ISStreamer"
	},

	author = "David Sulpy, Initial State Technologies",
	author_email = "david@initialstate.com",
	description = ("A python module to simplify the process of getting log data to Initial State's platform"),
	license = "MIT",
	keywords = "logger,logstream,initial state",
	url = "https://www.initialstate.com",
	
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Topic :: Utilities",
		"License :: OSI Approved :: MIT License"
	]
)