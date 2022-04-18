# Aitomatic CLI

The Command Line Interface (CLI) to create a project, build an image or deploy apps to Aitomatic cloud.

## Prerequisite

1. python3
2. pip

## Installing

To install this CLI tool you can run the below command

```shell
pip3 install aitomatic-cli
```

Alternatively, you clone this repo and then run this command from within the repository folder

```shell
pip3 install -e .
```

Both the above commands would install the package globally and `aito` will be available on your system.

## How to use

- `aito login`: Login to Aitomatic account 
- `aito app deploy`: Deploy app to Aitomatic cloud

## Feedback

In order to report issues, please open one in https://github.com/aitomatic/aitomatic-cli/issues


Temporary: If the deploy command failed due to change is service api. Update api base:

1. Clone https://github.com/aitomatic/ai-cloud
2. Follow instruction and select dev stack
3. Get the service host name
```
pulumi stack select dev
pulumi stack output kodaServiceHostname
```
4. Set AI_CLI_API_BASE env var to 
```
export AI_CLI_API_BASE = "http://" + <hostname from step 3>
```