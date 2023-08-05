import yaml
import sys
from collections import defaultdict
from schema import SchemaError
from cvascode.core.schema import schema


class DataIngestor():
    @staticmethod
    def ingest(filepaths):
        data = {}
        for filepath in filepaths:
            with open(filepath, 'r') as file:
                data.update(yaml.safe_load(file))
        DataIngestor._validate(data)
        data = DataIngestor._normalise(data)
        return defaultdict(lambda: None, data)

    @staticmethod
    def _validate(data):
        try:
            schema.validate(data)
        except SchemaError as e:
            print(e)
            sys.exit(2)

    @staticmethod
    def _normalise(data):
        if data.get('fullname') is None:
            data['fullname'] = " ".join([name for name in [
                data.get('firstname'),
                data.get('middlename'),
                data.get('lastname'),
            ] if name is not None])
        return data
