import re

from .arl_features import ARLFeatures
from .arl_rules import ARLRules
from .arl_conclusions import ARLConclusions
from .utils import get_str_order


class ARLHandler:
    SECTIONS = ['features', 'rules', 'conclusions', 'undefined_variables']

    def __init__(self, arl_dict: dict, mapping_data: dict = None) -> None:
        self.arl_dict = arl_dict
        if mapping_data is not None:
            self.map_data_variables(mapping_data)
        else:
            self.parse_handler_sections()

    @staticmethod
    def convert_arl_dict_to_str(arl_dict: dict) -> str:
        result = []
        for section, content in arl_dict.items():
            tmp_str = f'[{section}]\n{content}'
            result.append(tmp_str)
        return '\n\n'.join(result)

    @staticmethod
    def convert_arl_str_to_dict(arl_str: str) -> dict:
        result = {}
        arl_format = r'^\[(?P<section>[\w -]+)\][ ]*\n?'
        pieces = re.split(arl_format, arl_str, 0, re.MULTILINE)[1:]
        for i, txt in enumerate(pieces):
            if txt in ARLHandler.SECTIONS and i + 1 < len(pieces):
                result[txt.strip()] = pieces[i + 1].strip()
            elif txt in ARLHandler.SECTIONS:
                result[txt.strip()] = ''

        return result

    @property
    def arl_str(self):
        return self._arl_str

    @arl_str.setter
    def arl_str(self, value: str):
        if value == '':
            value = '\n\n'.join([f'[{x}]' for x in self.SECTIONS])

        # use some auto-formatting that occurs during dict setting, especially
        # to check for missing sections and create blanks
        self.arl_dict = ARLHandler.convert_arl_str_to_dict(value)

    @property
    def arl_dict(self):
        return self._arl_dict

    @arl_dict.setter
    def arl_dict(self, value: dict):
        value = value.copy()
        for k in self.SECTIONS:
            if k not in value.keys():
                value[k] = ''

        value = {k: v for k, v in value.items() if k in self.SECTIONS}
        self._arl_dict = value
        self._arl_str = ARLHandler.convert_arl_dict_to_str(value)
        self.parse_handler_sections()

    def map_data_variables(self, mapping_data: dict):
        """
        change feature names to data columns names based on passed mapping
        data_mapping should have format {feature_name : data_column_name, ...}
        """
        repl_order = get_str_order(mapping_data.keys())
        arl_str = self.arl_str
        for key in repl_order:
            arl_str = arl_str.replace(key, mapping_data[key])

        self.arl_str = arl_str

    def parse_handler_sections(self):
        self.features = ARLFeatures(self.arl_dict['features']).feature_dict
        self.rules = ARLRules(self.features, self.arl_dict['rules']).rule_dict
        self.conclusions = ARLConclusions(
            self.features, self.rules, self.arl_dict['conclusions']
        ).conclusion_dict

    def get_arl_for_conclusion(self, conclusion: str) -> 'ARLHandler':
        '''
        returns an ARLHandler with the arl parsed down to only the chosen
        conclusion
        '''
        if conclusion not in self.conclusions['conclusions']:
            raise ValueError(f'Conclusion {conclusion} not found')

        out = {}
        conc_str = ARLConclusions(
            self.features, self.rules, self.arl_dict['conclusions']
        ).conclusion_str

        for line in conc_str.splitlines():
            if line.startswith(conclusion):
                new_arl = self.arl_str.replace(conc_str, line)
                return ARLHandler(ARLHandler.convert_arl_str_to_dict(new_arl))

        raise ValueError(f'Unable to parse out conclusion {conclusion}')
