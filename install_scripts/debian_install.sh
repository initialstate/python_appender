#!/bin/bash

echo "Beginning ISStreamer Python Easy Installation!"


function check_for_easy_install {
    if hash easy_install 2>/dev/null; then
        easy_install_version=$(easy_install --version)
        echo "Found easy_install: $easy_install_version"
    else
        echo "easy_install not found, installing now..."

        if hash apt-get 2>/dev/null; then
        	apt-get -y install python-setuptools		
        else
        	echo "no apt-get, using curl..."
        	curl https://bootstrap.pypa.io/ez_setup.py -o - | python
        fi
    fi
}

function check_for_pip {
	if hash pip 2>/dev/null; then
		pip_version=$(pip --version)
		echo "Found pip: $pip_version"
	else
		echo "pip not found, installing now..."
		easy_install pip
	fi
}

function check_for_isstreamer {
	isstreamer=$(pip list | grep ISStreamer)
	if [ -z "$isstreamer" ]; then
		echo "ISStreamer not found, installing..."
		pip install ISStreamer --pre
	else
		echo "ISStreamer found, updating..."
		pip install --upgrade ISStreamer --pre
	fi
}

check_for_easy_install
check_for_pip
check_for_isstreamer

