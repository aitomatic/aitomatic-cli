import os
import json
import requests
from aitomatic.api.client import get_api_root, get_project_id, ProjectManager
from aitomatic.api import model_params as mp 
from aitomatic.dsl.arl_handler import ARLHandler
from typing import List, Any, Dict, Optional

API_TOKEN = os.getenv('AITOMATIC_API_TOKEN')


class ModelBuilder:

    def __init__(self, project_name=None, api_token=None):
        if api_token is None:
            api_token = os.getenv('AITOMATIC_API_TOKEN')

        if project_name is None:
            project_name = os.getenv('AITOMATIC_PROJECT_NAME')

        self.project = ProjectManager(project_name=project_name,
                                      api_token=api_token)
        self.headers = {
            'accept': 'application/json',
            'authorization': api_token,
            'conent-type': 'application/json',
        }
        self.init_endpoints()

    def init_endpoints(self):
        _, self.API_ROOT = get_api_root()
        self.MODEL_BUILD = f'{self.API_ROOT}/models'

    def get_existing_model_params(self, model_name: str):
        resp = self.project.get_model_info(model_name)
        model_input = resp['model_input']
        params = model_input.get('model_params')
        return params

    def build_model(
        self, model_type: str, model_name: str,
        knowledge_set_name: str,
        data_set_name: str, model_params: dict, 
        ml_models: List[Any] = [], 
        label_columns: Dict[str, Optional[Any]] = {},
        threshold: Any = {},
        membership_error_width: Any = {},
        mapping_data: Any = None,
        metadata: Any = None,
    ):
        if model_type not in mp.K1ST:
            raise ValueError(f'Invalid K1st model type {model_type}. '
                             f'Must be in {mp.K1ST}')

        if not self.is_model_name_unique(model_name):
            raise ValueError(f'model_name not unique. '
                             f'model_name must be unique to build new model')

        payload = {
            'model_type': model_type,
            'project': self.project.project_name,
            'model_name': model_name,
            'knowledge_set_name': knowledge_set_name,
            'data_set_name': data_set_name,
            'model_params': model_params,
            'ml_models': ml_models,
            'label_columns': label_columns,
            'threshold': threshold,
            'membership_error_width': membership_error_width,
            'mapping_data': mapping_data,
            'metadata': metadata
        }
        resp = self.project.make_request('post', self.MODEL_BUILD,
                                         json=payload)
        return resp

    def get_base_model_params(self, model_type: str, knowledge_set_name: str, **kwargs):
        knowledge = self.project.get_knowledge(knowledge_set_name)
        params = mp.K1STModelParams(model_type, knowledge_arl=knowledge,
                                    **kwargs)
        return params

    def is_model_name_unique(self, model_name: str):
        try:
            self.project.get_model_id(model_name)
            return False
        except ValueError:
            return True

