import os
import requests
from aitomatic.api.exceptions import MissingEnvironmentVariable

# TODO: Change default environment to production
os.environ['AITOMATIC_ENVIRONMENT'] = 'staging'

MODEL_API_ROOT = {
    'dev': 'https://model-api-dev.platform.aitomatic.com',
    'staging': 'https://model-api-stg.platform.aitomatic.com',
    'production': 'https://model-api-prod.platform.aitomatic.com',
}

CLIENT_API_ROOT = {
    'dev': 'https://dev.platform.aitomatic.com/api/client',
    'staging': 'https://staging.platform.aitomatic.com/api/client',
    'production': 'https://production.platform.aitomatic.com/api/client',
}

def set_environment(aitomatic_environment: str=None, api_access_token: str=None,
                    project_name: str=None):
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


def get_api_root(aitomatic_environment=None):
    if aitomatic_environment is None:
        aitomatic_environment = os.getenv('AITOMATIC_ENVIRONMENT')

    model_api_root = MODEL_API_ROOT.get(aitomatic_environment)
    client_api_root = CLIENT_API_ROOT.get(aitomatic_environment)
    return model_api_root, client_api_root


def get_project_id(project_name: str, api_token: str=None):
    if api_token is None:
        api_token = os.getenv('AITOMATIC_API_TOKEN')

    _, api_root = get_api_root()
    url = f'{api_root}/project'
    headers = {
        'authorization': api_token,
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    data = {'project_name': project_name}
    resp = requests.post(
        url,
        headers=headers,
        json=data
    )
    # Handle request errors
    if resp.status_code != 200:
        err = f'{resp.status_code}: {resp.content}'
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    id_ = resp_content['id']
    return id_


