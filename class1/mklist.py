#!/usr/bin/env python
####################################################################################################
'''
Simple program which takes a moderately involved Python list and outputs it in YAML and JSON
format
'''

# Imports
import json
import yaml

# Globals
YAML_FILE = 'mklist.yaml'
JSON_FILE = 'mklist.json'

__version__ = '0.0.1'


def yaml_output(list1, abroutform=True):
    with open(YAML_FILE, 'w') as f1:
        f1.write(yaml.dump(list1, default_flow_style=abroutform))

def json_output(list1):
    with open(JSON_FILE, 'w') as f1:
        json.dump(list1, f1)

if __name__ == '__main__':
    list1 = [1, 2, 3, 'one', 'two', 'three', {'a': 'apple', 'b': 'banana', 'c': 'clementine'}]

    print 'Example list:\n{}'.format(list1)
    yaml_output(list1, False)
    json_output(list1)

