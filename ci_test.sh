#!/bin/bash -xe

venv=python2.7

if [ "${TRAVIS_PYTHON_VERSION}" == "pypy" ]; then
	venv=pypy2
else
	venv=python${TRAVIS_PYTHON_VERSION}
fi

if [ "${venv}" == "pypy2" ]; then
    [ -f "/home/travis/virtualenv/pypy-5.4.1/bin/activate" ] && source /home/travis/virtualenv/pypy-5.4.1/bin/activate
else
    [ -f "/home/travis/virtualenv/${venv}/bin/activate" ] && source /home/travis/virtualenv/${venv}/bin/activate
fi

python --version

bash -xe starttest.sh $venv
