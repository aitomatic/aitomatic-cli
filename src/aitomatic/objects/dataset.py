class Dataset:
    raw_data: dict

    def __init__(self, raw_data) -> None:
        self.raw_data = raw_data

    @property
    def type(self) -> str:
        return self.raw_data.get('type', '')

    @property
    def metadata(self) -> dict:
        if self.type == 'DATA':
            return self.raw_data.get('dataset_metadata', {}).get('metadata', {})
        if self.type == 'DESCRIBE':
            obj = {}
            for var in self.raw_data.get('variables'):
                obj[var['name']] = var
            return obj
