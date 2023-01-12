import os
import sys
from typing import Dict, Tuple, Union, List

from tqdm import tqdm
from itertools import chain
import requests
import json
import pandas as pd
import numpy as np
import logging
from aitomatic.api import get_api_root, get_project_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class WebModel:
    """
    Class for making inference calls with models served via the Aitomatic Wed API

    Ex:
    model = WebModel(API_TOKEN, "MyModelName").load_params()
    predictions = model.predict({'X': MyDataFrame})
    """

    def __init__(self, model_name: str, api_token: str=None,
                 project_name: str=None, chunk_size: int=1024):
        """
        Initialize remote model

        :param api_token: Aitomatic API Access Token
        :param model_name: name of the model being used
        :param chunk_size: size to chunk inference calls in kb
        """
        if api_token is None:
            api_token = os.getenv('AITOMATIC_API_TOKEN')

        if project_name is None:
            project_name = os.getenv('AITOMATIC_PROJECT_NAME')
            project_id = os.getenv('AITOMATIC_PROJECT_ID')
        else:
            project_id = get_project_id(project_name)

        self.project_name = project_name
        self.project_id = project_id
        self.model_name = model_name
        self.api_token = api_token
        self.chunk_size = chunk_size * 1024 # convert from kb to bytes
        self.model_version = 'latest'
        self.headers = {
            'access-token': self.api_token,
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }
        self.init_endpoints()

    def init_endpoints(self):
        self.MODEL_API_ROOT, self.CLIENT_API_ROOT = get_api_root()
        self.MODELS_ENDPOINT = f'{self.MODEL_API_ROOT}/models'
        self.PREDICTION_ENDPOINT = f'{self.MODELS_ENDPOINT}/infer'
        self.METADATA_ENDPOINT = f'{self.MODELS_ENDPOINT}/metadata'
        self.METRICS_ENDPOINT = f'{self.MODELS_ENDPOINT}/metrics'
        self.MODEL_LIST_ENDPOINT = f'{self.CLIENT_API_ROOT}/{self.project_id}/models'

    def batch_predict(self, input_data: Dict) -> Dict:
        """
        Chunks data in input_data['X'] and does prediction in batches
        """
        # TODO: Make this more versatile to it slices all large data in input
        # data, not just 'X' ... maybe

        X = input_data['X']
        Xother = {k:deepcopy(v) for k,v in input_data.items() if k != 'X'}
        size = sys.getsizeof(X)
        items = self.count_items(X)
        chunk_max = self.chunk_size
        spi = size / items
        N = int(chunk_max / spi) - 1
        total_batches = int(np.ceil(items / N))
        logger.info(f'data size too large. Running inference in chunks of '
                    f'{chunk_max /1024} kb or {N} data points')
        out = []
        for Xi in tqdm(self.slice_data(X, N), total=total_batches):
            pred = self.predict({'X': Xi, **Xother})['predictions']
            out.append(pred)

        predictions = self.merge_items(out, type(X))
        return {'predictions': predictions}

    def merge_items(self, items, dtype):
        """
        Merge multiple inference outputs
        """
        if dtype == dict:
            tmp = [pd.DataFrame(x) for x in items]
            merged = pd.concat(tmp, axis=0)
            return merged.to_dict()
        elif dtype == np.ndarray:
            return np.concatenate(items)
        elif dtype == list:
            return list(chain.from_iterable(items))
        elif dtype == pd.DataFrame or dtype == pd.Series:
            return pd.concat(items, axis=0)
        else:
            raise NotImplementedError(f'Data type {str(type)} not supported')

    def count_items(self, X: Union[np.ndarray, pd.Series, pd.DataFrame, Dict, List]):
        """
        Count items in dataset
        """
        if hasattr(X, 'shape'):
            return X.shape[0]

        return len(X)

    def slice_data(self, X, N):
        """
        Iterate over slices of data with pieces of size N
        :param X: data, pd.DataFrame, pd.Series, np.ndarray, dict or list
        :param N: max number of items per slice
        """
        to_dict = False
        if isinstance(X, dict):
            to_dict = True
            X = pd.DataFrame(X)

        Ni = N
        Nj = 0
        Nmax = self.count_items(X)
        while Nj <= Nmax:
            tmp = X[Nj:Ni]
            if self.count_items(tmp) == 0:
                break

            if to_dict:
                yield tmp.to_dict()
            else:
                yield tmp

            Nj = Ni
            Ni = Ni + N

    def predict(self, input_data: Dict) -> Dict:
        """
        Logic to generate prediction from data

        :params input_data: input data for prediction, dictionary with data under key 'X'
        :return: a dictionary with key `predictions` containing the predictions
        """
        if sys.getsizeof(input_data['X']) > self.chunk_size + 1:
            return self.batch_predict(input_data)

        # Convert data to JSON safe dict
        #json_data, types_dict = convert_data_to_json(input_data)
        json_data, types_dict = convert_data_to_json(input_data['X'])

        # TODO: change API input to take dict with {'input_data': {'X': data}}
        # so that A) models can take additional dict parameters if needed and
        # B) appropriate type conversions can be done on response to return to
        # user the same input type that they put in

        # TODO: remove this, after resolving API input format
        types_dict['predictions']= type(input_data['X'])

        # Create web request dicts
        request_data = {
            'project_name': self.project_name,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'input_data': json_data
        }

        # Convert data to json str (NpEncoder allows numpy array conversion)
        request_data = json.dumps(request_data, cls=NpEncoder)

        # Make web request
        resp = requests.post(
            self.PREDICTION_ENDPOINT,
            headers=self.headers,
            data=request_data
        )

        # Handle request errors
        if resp.status_code != 200:
            err = f'{resp.status_code}: {resp.content}'
            raise ConnectionError(err)

        resp_content = json.loads(resp.content)
        # resp_data = resp_content['result']
        resp_data = resp_content
        result_file_path = resp_content['result_file_path']

        # Convert response back to correct types
        # predictions format to match input_data['X'] format/types
        predictions = convert_json_to_data(
            resp_data['result'], types_dict
        )

        return predictions

    def process(self, input_data: Dict) -> Dict:
        """
        Implement logic to generate prediction from data
        """
        return self.predict(input_data=input_data)

    def persist(self, version: str) -> str:
        raise NotImplementedError()

    def load_params(self, *args, **kwargs) -> 'WebModel':
        return self.load(*args, **kwargs)

    def load(self, version: str = 'latest') -> 'WebModel':
        """
        load model parameters for usage

        :param version: (optional) version of the model to load, defaults to
        latest
        """
        self.model_version = version

        # TODO: Make API call to get model stats & metrics, uncomment below
        # when API implemented

        resp = requests.get(
            self.METADATA_ENDPOINT,
            headers=self.headers,
            params={'project_name': self.project_name,
                    'model_name': self.model_name,
                    'model_version': version},
        )

        # Handle request errors
        if resp.status_code != 200:
            err = f'{resp.status_code}: {resp.content}'
            raise ConnectionError(err)

        resp_data = json.loads(resp.content)
        self.stats = resp_data['result']['stats']
        self.metrics = resp_data['result']['metrics']
        return self

    def _save_metrics(self):
        payload = {
            'project_name': self.project_name,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'metrics': self.metrics
        }
        resp = requests.post(
            self.METRICS_ENDPOINT,
            headers=self.headers,
            json=payload
        )

        if resp.status_code != 200:
            err = f'{resp.status_code}: {resp.content}'
            raise ConnectionError(err)

    def log_metrics(self, key, value):
        self.metrics[key] = value
        self._save_metrics()

    @staticmethod
    def get_model_names(api_token, project_name=None):
        headers = {
            'authorization': api_token,
            'Content-Type': 'application/json',
            'accept': 'application/json',
        }
        resp = requests.get(WebModel.MODEL_LIST_ENDPOINT, headers=headers)

        # Handle request errors
        if resp.status_code != 200:
            err = f'{resp.status_code}: {resp.content}'
            raise ConnectionError(err)

        resp_content = json.loads(resp.content)
        return [x['name'] for x in resp_content]


def convert_data_to_json(input_data: Dict) -> Tuple[Dict, Dict]:
    """
    Converts input data to json str for web request.
    Supports dict, pandas DataFrame, pandas Series and numpy arrays
    """
    # This segment is here when passing input_data['X'] instead of input_data
    # TODO: remove this after API is updated
    if isinstance(input_data, (pd.DataFrame, pd.Series)):
        return json.loads(input_data.to_json()), {'predictions': type(input_data)}
    elif isinstance(input_data, (dict, np.ndarray)) and 'X' not in input_data:
        return input_data, {'predictions': type(input_data)}

    out_data = {}
    types_dict = {}
    for k, v in input_data.items():
        types_dict[k] = type(v)
        if isinstance(v, (pd.DataFrame, pd.Series)):
            out_data[k] = json.loads(v.to_json())
        elif isinstance(v, dict):
            # no changes needed
            out_data[k] = v
        elif isinstance(v, np.ndarray):
            # Convert later using JSONEncoder NpEncoder
            out_data[k] = v
        else:
            out_data[k] = v

        if k.lower() in ['x', 'x_train', 'x_test']:
            types_dict['predictions'] = type(v)

    if 'predictions' not in types_dict.keys():
        types_dict['predictions'] = pd.DataFrame

    # out_json = json.dumps(out_data, cls=NpEncoder)
    return out_data, types_dict


def convert_json_to_data(json_data: Dict, types_dict: Dict) -> Dict:
    """
    converts json data input pandas Dataframe or pandas Series or numpy array
    depending on the types_dict generated when converting the input_data into
    json
    """
    out_data = {}
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    for k,v in json_data.items():
        goal_type = types_dict.get(k, pd.DataFrame)
        if goal_type == pd.DataFrame or goal_type == pd.Series:
            out_data[k] = goal_type(eval(v))
        elif goal_type == np.ndarray:
            out_data[k] = np.array(v, dtype='O')
        else:
            out_data[k] = v

    return out_data


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

