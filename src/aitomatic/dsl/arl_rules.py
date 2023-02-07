import re


class ARLRules:
    def __init__(self, feature_dict: dict, rules: str) -> None:
        self.feature_dict = feature_dict
        self.rule_str = rules

    @staticmethod
    def parse_rule_str_to_dict(rule_str: str, feature_dict: dict) -> dict:
        fmt = (
            '^(?P<var_name>[\w \-]+)(\[(?P<class>[\w -]+)\])? := '
            '(?P<def>[\w \.\-&|\(\)\[\]]+)($| for (?P<time_sign>[><=])'
            '(?P<time_val>\d+\.?\d*) (?P<time_unit>\w+))'
        )
        var_fmt = ' ?(?P<feature>[\w \.\-]+)(\[(?P<class>[\w -]+)\])? ?'

        missing_features = []
        missing_classes = []
        missing_rules = []
        defined_rules = set()
        parsed_rules = {}
        for i, line in enumerate(rule_str.splitlines()):
            if line.startswith('%'):
                # handle commented out lines
                continue

            tmp = re.match(fmt, line.strip())
            if tmp is None:
                raise SyntaxError(f'Syntax Error in Rules line {i+1}')

            tmp = tmp.groupdict()
            var_name = tmp['var_name'].strip()
            var_def = tmp['def'].strip()
            time_condition = {
                'sign': tmp.get('time_sign'),
                'value': tmp.get('time_val'),
                'unit': tmp.get('time_unit'),
            }

            ev_line = var_def
            fixed_line = var_def
            for m in re.finditer(var_fmt, var_def):
                tmp = m.groupdict()
                if tmp.get('class') is not None:
                    ft = tmp['feature'].strip()
                    cls = tmp['class'].strip()
                    if ft not in feature_dict['features'].keys():
                        missing_features.append((ft, i + 1))
                    elif cls not in feature_dict['features'][ft].keys():
                        missing_classes.append((ft, cls, i + 1))

                    ev_line = ev_line.replace(f'{ft}[{cls}]', 'True')
                    fixed_line = fixed_line.replace(f'{ft}[{cls}]', f'{ft}["{cls}"]')
                else:
                    alias = tmp['feature'].strip()
                    if alias == '':
                        continue

                    if alias not in defined_rules:
                        missing_rules.append((alias, i + 1))

                    ev_line = ev_line.replace(alias, 'True')

            try:
                eval(ev_line)
            except:
                raise SyntaxError(f'Syntax Error in Rules line {i+1}')

            defined_rules.add(var_name)
            parsed_rules[var_name] = {
                'raw_definition': var_def,
                'corrected_definition': fixed_line,
                'time_condition': time_condition,
            }

        missing = {
            'features': [{'feature': x, 'line': y} for x, y in missing_features],
            'classes': [
                {'feature': x, 'class': y, 'line': z} for x, y, z in missing_classes
            ],
            'rules': [{'rule': x, 'line': y} for x, y in missing_rules],
        }
        result = {'rules': parsed_rules, 'missing': missing}
        return result

    @property
    def rule_str(self):
        return self._rule_str

    @rule_str.setter
    def rule_str(self, value: str):
        self._rule_str = value
        self._rule_dict = ARLRules.parse_rule_str_to_dict(
            self._rule_str, self.feature_dict
        )

    @property
    def rule_dict(self):
        return self._rule_dict
