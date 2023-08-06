from yaml import load
from yaml import SafeLoader
from pathlib import Path

class ConfigHelper():
    def __init__(self) -> None:
        pass
    def load_yaml(self, yaml_file: str):
        if Path('my_file.yaml').suffix != '.yaml':
            raise ValueError('Input File not a .yaml File')
        with open(yaml_file) as f:
            data = load(f, Loader=SafeLoader)
        self.__dict__.update(**data)