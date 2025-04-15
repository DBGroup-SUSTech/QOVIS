#!/bin/bash

# python version 3.9
if [ -z "$(python3.9 --version | grep 'Python 3.9')" ]; then
    echo "Python: Check your python version and make sure execute \"python3.9 --version\" can return proper version like \"Python 3.9.13\""
else
    echo "Python ok"
fi

# python venv
if [ -z "$(python3.9 -m venv --help)" ]; then
    echo "Python venv: Check your python venv module and make sure execute \"python3.9 -m venv --help\" can return proper help message"
else
    echo "Python venv ok"
fi

# node v16
if [ -z "$(node -v | grep 'v16')" ]; then
    echo "Node: Check your node version and make sure execute \"node -v\" can return proper version like \"v16.18.1\""
else
    echo "Node ok"
fi
