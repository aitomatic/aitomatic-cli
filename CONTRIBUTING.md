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

1. Run `black` command to format code
```shell
black -S .
```
2. Run command to test script
```shell
python src/aitomatic.py
```

## Steps to install the CLI to virtual environment and test it

1. Run command to install CLI
```shell
pip install -e .
```
2. Verify the CLI
```shell
which aitomatic
```
3. Run `aitomatic` command
```shell
aitomatic
```

## Steps to package and distribute CLI to PyPI
