import os
import json
import requests
from aitomatic.api.exceptions import MissingEnvironmentVariable
from aitomatic.api.client import get_project_id

# TODO: Change default environment to production
os.environ['AITOMATIC_ENVIRONMENT'] = 'staging'


def set_environment(
    aitomatic_environment: str = None,
    api_access_token: str = None,
    project_name: str = None,
):
    '''
    Sets various parameters so you don't need to keep adding them to api
    function calls

    :param aitomatic_environment: whether to use the "dev", "stagining" or
    "production" servers for api calls
    :param api_access_token: personal api access token for aitomatic api
    :param project_name: name of project you want to work in. Models, data and
    knowledge are unique within a project
    '''
    if aitomatic_environment is not None:
        os.environ['AITOMATIC_ENVIRONMENT'] = aitomatic_environment

    if api_access_token is not None:
        os.environ['AITOMATIC_API_TOKEN'] = api_access_token

    if project_name is not None:
        os.environ['AITOMATIC_PROJECT_NAME'] = project_name
        project_id = get_project_id(project_name)
        os.environ['AITOMATIC_PROJECT_ID'] = project_id
