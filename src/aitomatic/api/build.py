import os
import json
import rquests
from aitomatic.api import get_api_root, get_project_id
from aitomatic.api import model_params as mp 

API_TOKEN = os.getenv('AITOMATIC_API_TOKEN')


class ModelBuilder:

    def __init__(self, project_name=None, api_token=None):
        if project_name is None:
            project_name = os.getenv('AITOMATIC_PROJECT_NAME')
            project_id = os.getenv('AITOMATIC_PROJECT_ID')
        else:
            project_id = get_project_id(project_name)

        if api_token is None:
            api_token = os.getenv('AITOMATIC_API_TOKEN')

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
        self.MODELS_LIST = f'{self.API_ROOT}/{self.project_id}/models'
        self.KNOWLEDGE_LIST = f'{self.API_ROOT}/{self.project_id}/knowledges'
        self.KNOWLEDGE_DETAIL = lambda id_: f'{self.API_ROOT}/knowledges/' + id_
        self.MODEL_DETAIL = lambda id_: f'{self.API_ROOT}/models/' + id_
        self.MODEL_BUILD = f'{self.API_ROOT}/models'


    def build_model(self, model_type: str, model_name: str,
                    knowledge_set_name: str,
                    data_set_name: str, model_params: dict):
        if model_type not in mp.K1ST_MODELS:
            raise ValueError(f'Invalid K1st model type {model_type}. '
                             f'Must be in {mp.K1ST_MODELS.keys()}')

        if not self.is_model_name_unique(model_name):
            raise ValueError(f'model_name not unique. '
                             f'model_name must be unique to build new model')

        payload = {
            'model_type': model_type,
            'project': self.project_name,
            'model_name': model_name,
            'knowledge_set_name': knowledge_set_name,
            'data_set_name': data_set_name,
            'model_params': model_params
        }
        resp = make_request('post', self.MODEL_BUILD, header=self.headers,
                            json=payload)
        return resp

    def is_model_name_unique(self, model_name: str):
        models = make_request('get', self.MODELS_LIST, headers=self.headers)
        names = [x['name'].lower() for x in models]
        if model_name.lower() in names:
            return False

        return True

    def get_knowledge_info(self, knowledge_set_name: str):
        id_ = self.get_knowledge_id(knowledge_set_name)
        data = make_request('get', self.KNOWLEDGE_DETAIL(id_), headers=self.headers)
        knowledge = data['knowledges']
        return knowledge

    def get_knowledge_id(self, knowledge_set_name: str):
        knowledges = make_request('get', self.KNOWLEDGE_LIST,
                                  headers=self.headers)
        id_ = [x['id'] for x in knowledges
               if x['name'].lower() == knowledge_set_name.lower()]
        if len(id_) == 0:
            raise ValueError(f'knowledge set {knowledge_set_name} not found.')

        return id_[0]


def make_request(request_type: str, url: str, **kwargs):
    func = requests.get(request_type)
    if func is None:
        raise ValueError(f'Invalid request type {request_type}. '
                         f'Must be get, post or put')

    resp = func(url, **kwargs)
    # Handle request errors
    if resp.status_code != 200:
        err = f'{resp.status_code}: {resp.content}'
        raise ConnectionError(err)

    resp_content = json.loads(resp.content)
    return resp_content
