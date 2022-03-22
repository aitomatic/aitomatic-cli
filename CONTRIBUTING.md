# Guide to contribute to this repository

## Prerequisite

1. python3
2. pip
3. virtualenv
```shell
pip install virtualenv
```

## Steps to setup dev environment

1. Create a python3 virtual environment
```shell
virtualenv .venv -p python3
```
2. Activate the virtual environment created in step 1
```shell
source .venv/bin/activate
```
3. Install `setuptools` to package code, `twine` to distribute package to PyPI and `black` to format python code
```shell
pip install setuptools twine black
```
4. Install libraries in file requirements.txt
```shell
pip install -r requirements.txt
```

## Steps to test code in local

## Steps to install the CLI to virtual environment and test it

1. Remove old CLI package in local
```shell
rm -rf .venv/bin/aitomatic aitomatic.egg-info
```
2. Run command to install CLI
```shell
python setup.py develop
```
3. Verify the CLI
```shell
which aitomatic
```
4. Run CLI hello command
```shell
aitomatic hello
```

## Steps to package and distribute CLI to PyPI
