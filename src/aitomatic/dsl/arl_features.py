import re
import numpy as np

from typing import Union
from .utils import str_to_value


class ARLFeatures:
    SEPERATOR = '\n\n'
    MEMBER_PREFIX = '--> '
    RESERVED_WORDS = ['min', 'max']

    def __init__(self, features: Union[str, dict]) -> None:
        if isinstance(features, str):
            self.feature_str = features
        elif isinstance(features, dict):
            self.feature_dict = features
        else:
            TypeError(f'Input must be dict or str, not {type(features)}')

    @staticmethod
    def parse_feature_str_to_dict(feature_str: str) -> dict:
        # remove commented out lines
        feature_str = '\n'.join(
            [line for line in feature_str.splitlines() if not line.startswith('%')]
        )

        pieces = feature_str.split(ARLFeatures.SEPERATOR)
        line_num = 0
        result = {'undefined': [], 'features': {}}

        for piece in pieces:
            try:
                seg_dict, undefined = ARLFeatures.parse_feature_segment(piece.strip())
            except SyntaxError as e:
                line_no = int(e.msg.split('line')[-1].strip())
                err_line = line_num + line_no
                raise SyntaxError(f'Syntax Error in Features line {err_line}') from e

            result['features'].update(seg_dict)
            result['undefined'].extend(undefined)
            line_num = line_num + len(piece.splitlines()) + 1

        # remove duplicates
        result['undefined'] = list(set(result['undefined']))
        return result

    @staticmethod
    def parse_feature_dict_to_str(feature_dict: dict) -> str:
        result = []
        undefined = feature_dict['undefined']
        for feat, classes in feature_dict['features'].items():
            tmp = f'{feat.strip()}\n'
            for cls, cls_def in classes.items():
                if 'is' in cls_def.keys():
                    v = cls_def['is']
                    if v not in undefined and isinstance(v, str):
                        v = f'"{v}"'
                    line = f'{cls} :: is {v}'

                elif 'min' in cls_def.keys() and 'max' in cls_def.keys():
                    line = f'{cls} :: {cls_def["min"]} to {cls_def["max"]}'

                tmp = tmp + ARLFeatures.MEMBER_PREFIX + line + '\n'

            result.append(tmp)

        return '\n'.join(result)

    @staticmethod
    def parse_feature_segment(segment: str):
        # Check that first line is feature name and rest of lines are membership classes
        feature_name_fmt = '^(?P<feature_name>[\w \.\-]+)$'
        feature_group_fmt = '--> (?P<group>[\w -]+) :: (?P<def>.+)'

        lines = segment.split('\n')
        feature_name_line = lines.pop(0).strip()
        # ignore commented out feature
        if feature_name_line.startswith('%'):
            return {}, {}

        feat_check = re.match(feature_name_fmt, feature_name_line)
        if feat_check is None:
            raise SyntaxError('Invalid Feature Name on line 1')

        # ignore commented lines
        lines = [line for line in lines if not line.startswith('%')]
        groups = [re.match(feature_group_fmt, line) for line in lines]
        if None in groups:
            idx = groups.index(None) + 2
            raise SyntaxError(f'Invalid membership definition on line {idx}')

        feature_name_line = feat_check.groupdict()['feature_name']
        result = {}
        result[feature_name_line] = {}
        undefined = []

        for i, grp in enumerate(groups):
            tokens = grp.groupdict()
            grp = tokens['group'].strip()
            grp_def = tokens['def'].strip()
            try:
                line_def = ARLFeatures.parse_feature_group_definition(grp_def)
            except Exception as e:
                raise SyntaxError(f'Invalid membership definition on line {i+2}') from e

            result[feature_name_line][grp] = line_def
            undefined.extend(line_def.pop('undefined'))

        return result, undefined

    @staticmethod
    def parse_feature_group_definition(grp_def: str):
        result = {}
        result['undefined'] = []

        if ' to ' in grp_def:
            format = '(?P<min>.+) to (?P<max>.+)'
            tokens = re.match(format, grp_def).groupdict()
            for k, v in tokens.items():
                if v in ARLFeatures.RESERVED_WORDS:
                    result[k] = v
                else:
                    x, undefined = str_to_value(v)
                    result[k] = x
                    if undefined:
                        result['undefined'].append(x)

            return result
        elif grp_def.startswith('is'):
            v = grp_def.split('is')[1].strip()
            x, undefined = str_to_value(v)
            result['is'] = x
            if undefined:
                result['undefined'].append(x)
        else:
            raise SyntaxError('Definition does not have an allowed form')

        return result

    @property
    def feature_str(self):
        return self._feature_str

    @feature_str.setter
    def feature_str(self, value: str):
        self.feature_dict = ARLFeatures.parse_feature_str_to_dict(value)

    @property
    def feature_dict(self):
        return self._feature_dict

    @feature_dict.setter
    def feature_dict(self, value: dict):
        fixed_features = ARLFeatures.complete_feature_classes(value['features'])
        value = value.copy()
        value['features'] = fixed_features

        self._feature_dict = value
        self._feature_str = ARLFeatures.parse_feature_dict_to_str(value)

    @staticmethod
    def complete_feature_classes(features: dict) -> dict:
        """
        for each numeric feature the membership classes must cover the full
        range from min to max
        """
        result = {}
        for feature, classes in features.items():
            if not ARLFeatures.is_feature_numeric(classes):
                continue

            fixed_classes = ARLFeatures.fix_class_ranges(classes)
            result[feature] = fixed_classes

        return result

    @staticmethod
    def is_feature_numeric(feature_members: dict) -> bool:
        """
        check if feature has numeric definitions
        """
        for cls, cls_def in feature_members.items():
            if 'min' in cls_def.keys() and 'max' in cls_def.keys():
                return True
            elif 'is' in cls_def.keys():
                val = cls_def['is']
                if isinstance(val, (int, float)):
                    return True

        return False

    @staticmethod
    def fix_class_ranges(feature_members: dict) -> dict:
        """
        check ranges of membership classes and identify which ranges are
        missing to complete the min to max coverage

        Assumes there are no undefined variables
        """
        ranges = []
        names = []
        repl = {'min': -np.inf, 'max': np.inf}

        for cls, cls_def in feature_members.items():
            if 'is' in cls_def.keys():
                val = cls_def['is']
                min_ = val
                max_ = val
            elif 'min' in cls_def.keys() and 'max' in cls_def.keys():
                min_ = cls_def['min']
                max_ = cls_def['max']
            else:
                raise ValueError('Invalid Class Definition')

            if isinstance(min_, str) and min_ in repl.keys():
                min_ = repl[min_]
            if isinstance(max_, str) and max_ in repl.keys():
                max_ = repl[max_]
            if isinstance(min_, str) or isinstance(max_, str):
                return feature_members

            ranges.append(sorted((min_, max_)))
            names.append(cls)

        names = sorted(names, key=lambda x: ranges[names.index(x)][0])
        ranges = sorted(ranges, key=lambda x: x[0])

        min_ = -np.inf
        all_ranges = []
        all_names = []
        class_n = 1

        for name, rng in zip(names, ranges):
            if rng[0] > min_:
                all_ranges.append([min_, rng[0]])
                all_names.append(f'class {class_n}')
                class_n += 1

            all_ranges.append(rng)
            all_names.append(name)
            class_n += 1

            if rng[1] > min_:
                min_ = rng[1]

        if min_ != np.inf:
            all_ranges.append([min_, np.inf])
            all_names.append(f'class {class_n}')

        result = {}
        for name, rng in zip(all_names, all_ranges):
            new_rng = []
            if rng[0] == -np.inf:
                new_rng.append('min')
            else:
                new_rng.append(rng[0])

            if rng[1] == np.inf:
                new_rng.append('max')
            else:
                new_rng.append(rng[1])

            if rng[0] == rng[1]:
                tmp = {'is': new_rng[0]}
            else:
                tmp = {'min': new_rng[0], 'max': new_rng[1]}

            result[name] = tmp

        return result
