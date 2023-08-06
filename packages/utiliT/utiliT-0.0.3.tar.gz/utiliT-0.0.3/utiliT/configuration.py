from yaml import load
from yaml import SafeLoader
from pathlib import Path
import json


class ConfigHelper(dict):

    def __init__(self) -> None:
        pass

    def load_dict(self, dictionary: dict):
        self.__dict__.update(**dictionary)
        self.update(dictionary)

    def load_yaml(self, yaml_file: str):
        if Path('my_file.yaml').suffix != '.yaml':
            raise ValueError('Input File not a .yaml File')
        with open(yaml_file) as f:
            data = load(f, Loader=SafeLoader)
        self.load_dict(data)

    def load_json(self, json_: str, json_string=False):
        if json_string:
            data = json.loads(json_)
        else:
            if Path('my_file.yaml').suffix != '.yaml':
                raise ValueError('Input File not a .json File')
            with open(json_) as f:
                data = json.load(f)
        self.load_dict(data)