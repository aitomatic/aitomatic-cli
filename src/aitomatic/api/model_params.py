import random
import json
from aitomatic.dsl.arl_handler import ARLHandler


class Params:
    def __init__(self, model_type: str, **kwargs):
        self.OUTPUT_KEYS = set(['model_type'])
        self.ALLOWED_PARAMS = MODEL_HYPER_PARAMS.get(model_type)
        if self.ALLOWED_PARAMS is None:
            raise ValueError(f'Invalid model_type')

        self.model_type = model_type
        for k, v in kwargs.items():
            if k in self.ALLOWED_PARAMS:
                self.add_param(k, v)

    def dict(self):
        out = {}
        for k in self.OUTPUT_KEYS:
            v = getattr(self, k)

            if isinstance(v, Params):
                out[k] = v.dict()
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], Params):
                out[k] = [x.dict() for x in v]
            else:
                out[k] = v

        return out

    def json(self, **kwargs):
        return json.dumps(self.dict(), **kwargs)

    def __str__(self):
        return self.json(indent=4)

    def add_param(self, key, value):
        if key not in self.ALLOWED_PARAMS:
            raise ValueError(
                f'parameter not allowed for model_type ' f'{self.model_type}'
            )

        allowed_value = self.ALLOWED_PARAMS.get(key)
        if isinstance(allowed_value, tuple) and isinstance(
            allowed_value[0], (int, float)
        ):
            # Check if value is in range
            if not isinstance(value, allowed_value[-1]):
                raise TypeError(
                    f'Invalid value type. Value must be {allowed_value[-1]}'
                )

            if value < allowed_value[0] or value > allowed_value[1]:
                raise ValueError(
                    f'Value outside allowed parameter range: ' f'{allowed_value}.'
                )

        elif isinstance(allowed_value, type) and not isinstance(value, allowed_value):
            raise TypeError(
                f'Expecting type {allowed_value}, got type ' f'{type(value)}'
            )

        setattr(self, key, value)
        self.OUTPUT_KEYS.add(key)

    def add_all_hyperparams(self):
        for k in self.OUTPUT_KEYS:
            v = getattr(self, k)
            if isinstance(v, Params):
                v.add_all_hyperparams()
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], Params):
                [x.add_all_hyperparams() for x in v]

        for k, v in self.ALLOWED_PARAMS.items():
            if hasattr(self, k):
                continue

            if isinstance(v, Params):
                if k == 'ensemble':
                    set_v = v(ENSEMBLE[0])
                else:
                    # TODO: Choose default intelligently
                    set_v = v(ML[0])

                set_v.add_all_hyperparams()
            elif isinstance(v, type):
                # if list or dict or str instantiate empty value
                set_v = v()
            elif isinstance(v, tuple):
                # if float or int with range choose random number in range
                min_ = v[0]
                max_ = v[1]
                if v[2] == float:
                    set_v = round(random.random() * (max_ - min_) + min_, 3)
                elif v[2] == int:
                    set_v = random.randint(min_, max_)

            self.add_param(k, set_v)


class K1STModelParams(Params):
    def __init__(self, model_type: str, knowledge_arl: ARLHandler, **kwargs):
        super().__init__(model_type)
        self.model_type = model_type
        defaults = K1ST_MODEL_DEFAULTS.get(model_type, {}).copy()
        defaults.update(kwargs)
        self.ALLOWED_PARAMS = {}
        self.OUTPUT_KEYS = set()
        self.renamed = {}
        self.knowledge = knowledge_arl
        if knowledge_arl is not None:
            self.add_params_from_arl(knowledge_arl, **defaults)

    def dict(self):
        tmp = super().dict()
        out = {}
        for k in tmp.keys():
            k2 = self.renamed.get(k)
            if k2 is not None:
                out[k2] = tmp[k]
            else:
                out[k] = tmp[k]

        return out

    def add_params_from_arl(self, arl: ARLHandler, **kwargs):
        for conclusion in arl.conclusions['conclusions'].keys():
            params = get_param_class(self.model_type, knowledge_arl=arl)
            for k, v in kwargs.items():
                allowed = params.ALLOWED_PARAMS.get(k)
                if allowed is None:
                    raise ValueError(f'Invalid parameter {k}')

                if isinstance(allowed, str) and isinstance(v, str):
                    params.add_param(k, v)
                elif isinstance(v, list):
                    v_params = [get_param_class(x, knowledge_arl=arl) for x in v]
                    params.add_param(k, v_params)
                elif isinstance(v, str):
                    v_params = get_param_class(v, knowledge_arl=arl)
                    params.add_param(k, v_params)

            if ' ' in conclusion:
                old_name = conclusion
                conclusion = conclusion.replace(' ', '_')
                self.renamed[conclusion] = old_name

            self.ALLOWED_PARAMS[conclusion] = Params
            self.add_param(conclusion, params)

    def get_conclusion_params(self, conclusion):
        if conclusion in self.renamed.values():
            conclusion = [k for k, v in self.renamed.items() if v == conclusion]
            if len(conclusion) == 0:
                raise ValueError('Conclusion not found')

            conclusion = conclusion[0]

        return getattr(self, conclusion)


def get_param_class(model_type, **kwargs):
    params = MODEL_PARAMS.get(model_type, Params)
    return params(model_type, **kwargs)


class FuzzyParams(Params):
    def __init__(self, model_type, knowledge_arl: ARLHandler):
        super().__init__(model_type)
        self.knowledge = knowledge_arl

    def add_all_hyperparams(self):
        super().add_all_hyperparams()
        membership_error = {}
        for feature, v in self.knowledge.features['features'].items():
            membership_error[feature] = {}
            for cls in v.keys():
                membership_error[feature][cls] = round(random.random(), 3)

        self.add_param('membership_error_width', membership_error)


K1ST_MODEL_DEFAULTS = {
    'COLLABORATOR': {'knowledge': ['fuzzy'], 'ml': ['XGBClassifier'], 'ensemble': 'OR'},
    'ORACLE': {
        'teacher': ['fuzzy'],
        'students': ['LogisticRegression', 'RandomForest'],
        'ensemble': 'MajorityVoting',
    },
}

MODEL_HYPER_PARAMS = {
    'COLLABORATOR': {
        'label_col': str,
        'knowledge': list,
        'ml': list,
        'ensemble': Params,
    },
    'ORACLE': {'teacher': list, 'students': list, 'ensemble': Params},
    'fuzzy': {'threshold': (0, 1, float), 'membership_error_width': dict},
    'XGBClassifier': {
        'threshold': (0, 1, float),
        'n_estimators': (5, 100, int),
        'max_depth': (1, 10, int),
        'eta': (0.001, 0.5, float),
    },
    'CNNClassifier': {
        'n_classes': (2, 30, int),
        'classifier_activation': str,
        'n_wrap': (1, 1000, int),
        'learning_rate': (0.001, 0.5, float),
        'batch_size': (1, 500, int),
        'epochs': (1, 1e6, int),
    },
    'LogisticRegression': {},
    'RandomForest': {},
    'OR': {},
    'MajorityVoting': {},
}

ENSEMBLE = ['OR', 'MajorityVoting']
ML = ['LogisticRegression', 'RandomForest', 'XGBClassifier', 'CNNClassifier']
KNOWLEDGE = ['fuzzy']
K1ST = ['COLLABORATOR', 'ORACLE']


MODEL_PARAMS = {
    #'ORACLE': OracleParams,
    #'K-COLLABORATOR': CollaboratorParams,
    'fuzzy': FuzzyParams
}
