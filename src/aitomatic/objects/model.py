class Model:
    raw_data: dict
    model_input: dict

    def __init__(self, raw_data: dict) -> None:
        self.raw_data = raw_data
        self.model_input = raw_data.get('model_input', {})

    @property
    def name(self):
        return self.raw_data.get('name', '')

    @property
    def data_name(self):
        return self.raw_data.get('dataset_name')

    @property
    def model_input_data(self) -> dict:
        return self.model_input.get('data', {})

    @property
    def schema_mapping(self) -> dict:
        return self.model_input_data.get('schema_mapping')

    @property
    def label_columns_mapping(self) -> dict:
        return self.model_input_data.get('label_column_name')

    @property
    def submodel(self) -> dict:
        return self.model_input.get('model', {}).get('submodel', {})

    @property
    def knowledge_model(self) -> dict:
        return self.submodel.get('knowledge_model', {})

    @property
    def ml_models(self) -> dict:
        return self.submodel.get('ml_models', [])

    @property
    def metadata(self) -> dict:
        return self.knowledge_model.get('hyperparams', {}).get('feature_range', {})

    @property
    def model_output(self) -> dict:
        return self.raw_data.get('model_output', {})

    @property
    def status(self) -> str:
        return self.raw_data.get('status', '')

    @property
    def architect(self) -> str:
        return self.raw_data.get("model_type")

    @property
    def structured_knowledge_name(self):
        return self.raw_data.get('structured_knowledge_name')
