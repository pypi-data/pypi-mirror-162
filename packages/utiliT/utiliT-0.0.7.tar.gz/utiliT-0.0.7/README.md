# utiliT

## Description

This package serves as a wrapper for many other packages and serves to help streamline a lot of mundane and repetitive tasks so you can focus on thinking rather than googling how to read a yaml file. 

## Installation

To install this toolkit, simply run

```
pip install utiliT
```

## Usage

### IO

One main use case for utiliT is to simplify file reading and writing. Instead of having to import multiple packages and deal with `open` statements, `utiliT.io` helps simplify this and reading and writing YAML, TOML, JSON, TXT, and Pickle files can be done in one line

**YAML, TOML, JSON Reading:**
This toolbox can help to read YAML, TOML, and JSON files in as dictionaries. Additionally, there are functions to write each of these to
Using the functions for YAML, TOML, and JSON reading and writing are extremely similar (the only difference being the function names) and a demonstration with YAML files is shown below.

```python
from utiliT.io import read_yaml, dump_yaml

# Reading from file
data = read_yaml('file.yaml')

# Reading from string
yaml_string = "..."
data = read_yaml(yaml_string, string = True)

# Writing to file
dump_yaml(data, 'file.yaml')

# Writing to string
yaml_string = dump_yaml(data)
```

Replace the `read_yaml` function with `read_toml` or `read_json` and replace `dump_yaml` with `dump_toml` and `dump_json` to read/write TOML and JSON files respectively. The function parameters do not change.


**ConfigHelper:** Along with reading YAML, JSON, and TOML files, `utilit.io` offers a `ConfigHelper` class that extends a dictionary. This class allows you to organize any configuration you have into a single object and access passed in values through key-value pairs and as class variables. This class can load in YAML, TOML, and JSON files / strings along with traditional dictionaries. 

Demo: 
Our YAML file (`file.yaml`)
```YAML
foo: 'bar'
fizz: 'buzz'
```

```python
from utilit.io import ConfigHelper

c = ConfigHelper()
c.load_yaml('file.yaml')

## Both of these will display 'bar'
print(c.foo)
print(c['foo'])
```
As this extends a dictionary, traditional dictionary operations can also be performed on it. Additionally, the contents of this object can be written to a YAML, JSON, or TOML file or string.

```python
c.dump_yaml('file.yaml')
c.dump_json('file.json')
c.dump_toml('file.toml')
```

If no file name is passed into this, these functions will output a string. 


**TXT Files:**
You can also use `read_txt` to read the text in files line by line. You have the option to get an array of the lines as strings, or a single string with the contents of the entire document.
You can also use `dump_txt` to dump an array of strings and a single string.

```python
from utiliT.io import read_txt, dump_txt

#Read as array of strings
data = read_txt('file.txt')

#Write array of strings to file
data = dump_txt(data, 'file.txt')

# Read everything into one string
data = read_txt('file.txt', string = True)

#Write a string to a file. Its the same code as writing an array of strings
data = dump_txt(data, 'file.txt')

```

**Pickle Files:**
`utiliT` also makes reading and writing pickle files easy!

```python
from utiliT.io import read_pickle, dump_pickle

#Read a pickle object
object_ = read_pickle('object.pickle')

# Write a pickle object
dump_pickle(object_, 'object.pickle')

```


## Contact

Contact Nakul Upadhya at nakulupadhya1@gmail.com
