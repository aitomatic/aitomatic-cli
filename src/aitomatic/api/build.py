import os
import time
import pandas as pd
from aitomatic.api.client import get_api_root, ProjectManager
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

        self.project = ProjectManager(project_name=project_name, api_token=api_token)
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
        self,
        model_type: str,
        model_name: str,
        knowledge_set_name: str,
        data_set_name: str,
        ml_models: List[Any] = [],
        label_columns: Dict[str, Optional[Any]] = {},
        threshold: Any = {},
        membership_error_width: Any = {},
        mapping_data: Any = None,
        metadata: Any = None,
    ):
        if model_type not in mp.K1ST:
            raise ValueError(
                f'Invalid K1st model type {model_type}. ' f'Must be in {mp.K1ST}'
            )

        if not self.is_model_name_unique(model_name):
            raise ValueError(
                f'model_name not unique. '
                f'model_name must be unique to build new model'
            )

        payload = {
            'model_type': model_type,
            'project': self.project.project_name,
            'model_name': model_name,
            'knowledge_set_name': knowledge_set_name,
            'data_set_name': data_set_name,
            'model_params': {},
            'ml_models': ml_models,
            'label_columns': label_columns,
            'threshold': threshold,
            'membership_error_width': membership_error_width,
            'mapping_data': mapping_data,
            'metadata': metadata,
        }
        resp = self.project.make_request('post', self.MODEL_BUILD, json=payload)
        return resp

    def get_base_model_params(self, model_type: str, knowledge_set_name: str, **kwargs):
        knowledge = self.project.get_knowledge(knowledge_set_name)
        params = mp.K1STModelParams(model_type, knowledge_arl=knowledge, **kwargs)
        return params

    def is_model_name_unique(self, model_name: str):
        try:
            self.project.get_model_id(model_name)
            return False
        except ValueError:
            return True

    def get_default_membership_error_widths(self, knowledge: ARLHandler):
        error_widths = {}

        for feat, classes in knowledge.features['features'].items():
            # Make all options for 1 conclusion model
            # min_ = metadata[col]['min']
            # max_ = metadata[col]['max']
            for cls, rng in classes.items():
                if not error_widths.get(feat):
                    error_widths[feat] = {}
                error_widths[feat][cls] = 1

        return error_widths

    def build_threshold_param_by_ranges(
        self, knowledge: ARLHandler, threshold_ranges: List[float]
    ):
        conclusions = knowledge.conclusions.get('conclusions', {}).keys()
        conclusion_threshold_hyperparms = [
            {k: value for k in conclusions} for value in threshold_ranges
        ]

        return conclusion_threshold_hyperparms

    def tune_model_with_hyperparams(
        self,
        tuning_params: List[Any],
        base_name: str,
        model_type: str,
        knowledge_name: str,
        data_name: str,
        mapping_data: Any,
        label_columns: Any,
        metadata: Any,
    ) -> pd.DataFrame:

        model_log = []
        print('Creating training jobs')
        for i, item in enumerate(tuning_params):
            test_params = {**item}
            model_name = f'{base_name} {i}'
            resp = self.build_model(
                model_type,
                model_name,
                knowledge_name,
                data_name,
                mapping_data=mapping_data,
                label_columns=label_columns,
                metadata=metadata,
                **item,
            )
            print(f'Training model {model_name}: {resp["id"]}')
            test_params['id'] = resp['id']
            test_params['model_name'] = model_name
            model_log.append(test_params)
        model_df = pd.DataFrame(model_log)
        model_df['status'] = 'training'
        return model_df

    def check_model_status(self, model_name):
        try:
            model_info = self.project.get_model_info(model_name)
            return model_info.status.lower()
        except Exception as e:
            print('Checking model status, e =', e)
            return 'training'

    def wait_for_tuning_to_complete(self, model_df: pd.DataFrame, sleep_time: int = 30):
        print('Waiting for training jobs to complete')
        while True:
            for i, row in model_df.iterrows():
                model_name = row['model_name']
                status = self.check_model_status(model_name)
                model_df.loc[i, 'status'] = status

            success_length = len(model_df[model_df['status'] == 'success'])
            error_length = len(model_df[model_df['status'] == 'error'])
            df_length = len(model_df)
            print(
                f'Waiting for training jobs to complete: [{success_length} success, {error_length} error, {df_length} total]'
            )
            if model_df['status'].isin(['training']).any():
                time.sleep(sleep_time)
            else:
                break
        return model_df


class MLParamBuilder:
    def build_xgb_param(
        self,
        n_estimators: int = 3,
        threshold: float = 0.5,
        max_depth: int = 4,
        eta: float = 0.001,
    ):
        return {
            'type': 'XGBClassifier',
            'hyperparams': {
                'n_estimators': n_estimators,
                'threshold': threshold,
                'max_depth': max_depth,
                'eta': eta,
            },
        }

    def builld_logistic_regression_param(
        self,
        # threshold: float = 0.5,
        # C: float = 1.0,
        # penalty: str = 'l2'
    ):
        return {
            'type': 'LogisticRegression',
            'hyperparams': {
                # 'threshold': threshold,
                # 'C': C,
                # 'penalty': penalty,
            },
        }

    def build_random_forest_param(
        self,
        # n_estimators: int = 3,
        # threshold: float = 0.5,
        # max_depth: int = 4
    ):
        return {
            'type': 'RandomForestClassifier',
            'hyperparams': {
                # 'n_estimators': n_estimators,
                # 'threshold': threshold,
                # 'max_depth': max_depth,
            },
        }

    def build_with_type(self, model_type: str, **kwargs):
        if model_type == 'XGBClassifier':
            return self.build_xgb_param(**kwargs)
        elif model_type == 'LogisticRegression':
            return self.builld_logistic_regression_param(**kwargs)
        elif model_type == 'RandomForestClassifier':
            return self.build_random_forest_param(**kwargs)
        else:
            raise ValueError(f'Unknown model type: {model_type}')
