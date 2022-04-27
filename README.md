# Aitomatic CLI

The Command Line Interface (CLI) to create a project, build an image or deploy apps to Aitomatic cloud.

## Prerequisite

1. python3
2. pip

## Installing

To install this CLI tool you can run the below command

```shell
pip3 install aitomatic
```

Alternatively, you clone this repo and then run this command from within the repository folder

```shell
pip3 install -e .
```

Both the above commands would install the package globally and `aito` will be available on your system.

## How to use

- `aito login`: Login to Aitomatic cloud
- `aito logout`: Logout from Aitomatic cloud 
- `aito deploy app <app_name>`: Deploy app to Aitomatic cluster
- `aito execute app <app_name>`: Execute app in Aitomatic cluster

## Feedback

In order to report issues, please open one in https://github.com/aitomatic/aitomatic-cli/issues
