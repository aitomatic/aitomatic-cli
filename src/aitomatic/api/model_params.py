K1ST_MODELS = {
    'K-COLLABORATOR': {
        'label_col': str,
        'knowledge': list,
        'ml': list,
        'ensemble': dict,
    },
    'ORACLE': {
        'teacher': dict,
        'students': list,
        'ensemble': dict,
    },
}

MODEL_HYPER_PARAMS = {
    'K-COLLABORATOR': {
        'label_col': str,
        'knowledge': list,
        'ml': list,
        'ensemble': dict,
    },
    'ORACLE': {
        'teacher': dict,
        'students': list,
        'ensemble': dict,
    },
    'fuzzy': {
        'threshold': [0,1],
        'membership_error_width': dict,
    }
    'XGBClassifier': {
        'threshold': [0, 1],
        'n_estimators': [5, 100],
        'max_depth': [1,10],
        'eta': [0.001, 0.5]
    },
    'LogisticRegression': {},
    'RandomForest': {},
    'OR': {},
    'MajorityVoting': {}
}

class Params:
    def __init__(self, model_type: str):
        self.OUTPUT_KEYS = ['model_type']
        self.ALLOWED_PARAMS = MODEL_HYPER_PARAMS.get(model_type)
        if self.ALLOWED_PARAMS is None:
            raise ValueError(f'Invalid model_type')

        self.model_type = model_type

    def dict(self):
        out = {
            k: getattr(self, k) for k in self.OUTPUT_KEYS
        }
        return out

    def json(self):
        return json.dumps(self.dict())

    def add_param(self, key, value):
        if key not in self.ALLOWED_PARAMS:
            raise ValueError(f'parameter not allowed for model_type '
                             f'{self.model_type}')

        allowed_value = self.ALLOWED_PARAMS.get(key)
        if (isinstance(allowed_value, list) and
                isinstance(allowed_value[0], (int, float))):
            # Check if value is in range
            if not isinstance(value, (int, float)):
                raise TypeError('Invalid value type. Value must be int or float.')

            if value < min(allowed_value) or value > max(allowed_value):
                raise ValueError(f'Value outside allowed parameter range: '
                                 f'{allowed_value}.')

        elif isinstance(allowed_value, type) and not isinstance(value, allowed_value):
            raise TypeError(f'Expecting type {allowed_value}, got type '
                            f'{type(value)}')

        setattr(self, key, value)
        self.OUTPUT_KEYS.append(key)


class ModelParams(Params):


    def __init__(self, model_type: str, model_name: str,
                 knowledge_set_name: str data_set_name: str,
                 project_name: str=None):
        super().__init__()
        self.OUTPUT_KEYS.extend(
            ['project', 'model_name', 'knowledge_set_name', 'data_set_name',
             'model_params']
        )
        if project_name is None:
            project_name = os.getenv('AITOMATIC_PROEJCT_NAME')

        self.model_type = model_type
        self.project = project_name
        self.model_name = model_name
        self.knowledge_set_name = knowledge_set_name
        self.data_set_name = data_set_name
        self.model_params = {}


class SubModelParams(Params):

    OUTPUT_KEYS = ['model_type']

    def __init__(self, model_type: str):
        super().__init__()
        self.model_type = model_type


