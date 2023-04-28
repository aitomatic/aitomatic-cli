import requests
import json
import os
from aitomatic.dsl.arl_handler import ARLHandler
from aitomatic.objects.model import Model
from aitomatic.objects.dataset import Dataset


MODEL_API_ROOT = {
    'local': 'http://localhost:8000/',
    'dev': 'https://model-api-dev.platform.aitomatic.com',
    'staging': 'https://model-api-stg.platform.aitomatic.com',
    'production': 'https://model-api-prod.platform.aitomatic.com',
}

CLIENT_API_ROOT = {
    'local': 'http://localhost:8000/api/client',
    'dev': 'https://dev.platform.aitomatic.com/api/client',
    'staging': 'https://staging.platform.aitomatic.com/api/client',
    'production': 'https://production.platform.aitomatic.com/api/client',
}


def get_api_root(aitomatic_environment=None):
    if aitomatic_environment is None:
        aitomatic_environment = os.getenv('AITOMATIC_ENVIRONMENT')

    model_api_root = MODEL_API_ROOT.get(aitomatic_environment)
    client_api_root = CLIENT_API_ROOT.get(aitomatic_environment)
    return model_api_root, client_api_root


def get_project_id(project_name: str, api_token: str = None):
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
    resp = requests.post(url, headers=headers, json=data)
    # Handle request errors
    if resp.status_code != 200:
        err = f'{resp.status_code}: {resp.content}'
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    id_ = resp_content['id']
    return id_


class ProjectManager:
    def __init__(self, project_name: str = None, api_token: str = None):
        if api_token is None:
            api_token = os.getenv('AITOMATIC_API_TOKEN')

        if project_name is None:
            project_name = os.getenv('AITOMATIC_PROJECT_NAME')
            project_id = os.getenv('AITOMATIC_PROJECT_ID')
        else:
            project_id = get_project_id(project_name, api_token=api_token)

        self.project_name = project_name
        self.project_id = project_id
        self.headers = {
            'accept': 'application/json',
            'authorization': api_token,
            'conent-type': 'application/json',
        }
        self.init_endpoints()

    def init_endpoints(self):
        _, self.API_ROOT = get_api_root()
        self.KNOWLEDGE_LIST = f'{self.API_ROOT}/{self.project_id}/knowledges'
        self.KNOWLEDGE_DETAIL = lambda id_: f'{self.API_ROOT}/knowledges/' + id_
        self.MODELS_LIST = f'{self.API_ROOT}/{self.project_id}/models'
        self.MODEL_DETAIL = lambda id_: f'{self.API_ROOT}/models/' + id_
        self.MODEL_BUILD = f'{self.API_ROOT}/models'
        self.DATA_LIST = f'{self.API_ROOT}/{self.project_id}/data'
        self.DATA_DETAIL = lambda id_: f'{self.API_ROOT}/data/' + id_

    def get_model_info(self, model_name: str):
        id_ = self.get_model_id(model_name)
        resp = self.make_request('get', self.MODEL_DETAIL(id_))
        if resp:
            model = Model(resp)
            return model

    def get_model_id(self, model_name: str):
        model_list = self.make_request('get', self.MODELS_LIST)
        id_ = [x['id'] for x in model_list if x['name'].lower() == model_name.lower()]
        if len(id_) == 0:
            raise ValueError(f'model {model_name} not found.')

        return id_[0]

    def get_data_info(self, data_name: str):
        id_ = self.get_data_id(data_name)
        resp = self.make_request('get', self.DATA_DETAIL(id_))
        if resp:
            return Dataset(resp)

    def get_data_id(self, data_name: str):
        data_list = self.make_request('get', self.DATA_LIST)
        id_ = [x['id'] for x in data_list if x['name'].lower() == data_name.lower()]
        if len(id_) == 0:
            raise ValueError(f'Dataset {data_name} not found.')

        return id_[0]

    def make_request(self, request_type: str, url: str, headers=None, **kwargs):
        if headers is None:
            headers = self.headers

        return make_request(request_type, url, headers=headers, **kwargs)

    def get_knowledge_info(self, knowledge_set_name: str) -> dict:
        id_ = self.get_knowledge_id(knowledge_set_name)
        data = make_request('get', self.KNOWLEDGE_DETAIL(id_), headers=self.headers)
        return data

    def get_knowledge(self, knowledge_set_name: str) -> ARLHandler:
        knowledge = self.get_knowledge_info(knowledge_set_name)['structured']
        return ARLHandler(knowledge)

    def get_knowledge_id(self, knowledge_set_name: str):
        knowledges = make_request('get', self.KNOWLEDGE_LIST, headers=self.headers)
        id_ = [
            x['id']
            for x in knowledges
            if x['name'].lower() == knowledge_set_name.lower()
        ]
        if len(id_) == 0:
            raise ValueError(f'knowledge set {knowledge_set_name} not found.')

        return id_[0]

    # TODO: Move to model builder class

    def get_base_conclusion_mapping(self, knowledge: ARLHandler):
        return {k: None for k in knowledge.conclusions.get('conclusions', {}).keys()}

    def get_base_metadata(self, dataset: Dataset, model: Model):
        schema_mapping = model.schema_mapping

        result = {}
        dataset_metadata = dataset.metadata
        for key in schema_mapping:
            if dataset_metadata.get(schema_mapping.get(key)):
                result[key] = dataset_metadata.get(schema_mapping.get(key))

        return result


def make_request(request_type: str, url: str, **kwargs):
    func = getattr(requests, request_type)
    if func is None:
        raise ValueError(
            f'Invalid request type {request_type}. ' f'Must be get, post or put'
        )

    resp = func(url, **kwargs)
    # Handle request errors
    if resp.status_code != 200:
        err = f'{resp.status_code}: {resp.content}'
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    return resp_content
