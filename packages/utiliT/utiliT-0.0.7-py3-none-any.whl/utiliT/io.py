from array import array
from io import StringIO
import yaml
from pathlib import Path
import json
import pickle
import toml
import ez_yaml


class ConfigHelper(dict):

    def __init__(self) -> None:
        pass

    def load_dict(self, dictionary: dict):
        self.__dict__.update(**dictionary)
        self.update(dictionary)

    def load_yaml(self, yaml_: str, string=False):
        if string:
            data = yaml.safe_load(yaml_)
        else:
            with open(yaml_, 'rb') as f:
                data = yaml.load(f, Loader=yaml.SafeLoader)
        self.load_dict(data)

    def load_json(self, json_: str, string=False):
        if string:
            data = json.loads(json_)
        else:
            with open(json_, 'rb') as f:
                data = json.load(f)
        self.load_dict(data)

    def load_toml(self, toml_: str, string=False):
        if string:
            data = toml.loads(toml_)
        else:
            with open(toml_, 'rb') as f:
                data = toml.load(f)
        self.load_dict(data)

    def dump_yaml(self, yaml_ = None):
        data = self.__dict__
        if yaml_ is None:
            return ez_yaml.to_string(data)
        else:
            with open(yaml_, 'wb') as f:
                yaml.dump(data, f)

    def dump_json(self, json_=None):
        data = self.__dict__
        if json_ is None:
            return json.dumps(data)
        else:
            with open(json_, 'wb') as f:
                json.dump(data, f)

    def dump_toml(self, toml_=None):
        data = self.__dict__
        if toml_ is None:
            return toml.dumps(data)
        else:
            with open(toml_, 'wb') as f:
                toml.dump(data, f)


def read_pickle(file_name):
    if Path(file_name).suffix != '.pickle':
        raise ValueError('File Name not a .pickle File')
    with open(file_name, 'rb') as f:
        data = pickle.load(f)
    return data


def dump_pickle(object, file_name):
    if Path(file_name).suffix != '.pickle':
        raise ValueError('File Name not a .pickle File')
    with open(file_name, 'wb') as f:
        pickle.dump(object, f)


def read_txt(file_name, string=False):
    with open(file_name, 'rb') as f:
        lines = f.readlines()
    if string:
        return '\n'.join(lines)
    return lines


def dump_txt(data, file_name):
    if type(data) is str:
        write = data
    else:
        write = "\n".join(data)
    with open(file_name, 'wb') as f:
        f.writelines(write)


def read_yaml(yaml_, string=False):
    if string:
        data = yaml.safe_load(yaml_)
    else:
        with open(yaml_, 'rb') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    return data


def read_json(json_, json_string=False):
    if json_string:
        data = json.loads(json_)
    else:
        with open(json_, 'rb') as f:
            data = json.load(f)
    return data


def read_toml(toml_: str, toml_string=False):
    if toml_string:
        data = toml.loads(toml_)
    else:
        with open(toml_, 'rb') as f:
            data = toml.load(f)
    return data


def dump_yaml(data, yaml_=None):
    if yaml_ is None:
        return ez_yaml.to_string(data)
    else:
        with open(yaml_, 'wb') as f:
            yaml.dump(data, f)


def dump_json(data, json_=None):
    if json_ is None:
        return json.dumps(data)
    else:
        with open(json_, 'wb') as f:
            json.dump(data, f)


def dump_toml(data, toml_=None):
    if toml_ is None:
        return toml.dumps(data)
    else:
        with open(toml_, 'wb') as f:
            toml.dump(data, f)