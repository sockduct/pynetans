#!/usr/bin/env python
####################################################################################################
'''
Simple program which reads in a list from a YAML and a JSON file
'''

# Imports
import json
from pprint import pprint
import yaml

# Globals
BASE_FILE = 'exercise6'
YAML_FILE = BASE_FILE + '.yaml'
YAML_BOF = '---\n'
JSON_FILE = BASE_FILE + '.json'

__version__ = '0.0.1'


def yaml_input(file1):
    with open(file1) as f1:
        list1 = yaml.load(f1)
    return list1

def json_input(file1):
    with open(file1) as f1:
        list1 = json.load(f1)
    return list1

def ppfiles(yaml_file, json_file, pretty=True):
    list1 = yaml_input(yaml_file)
    print "List read from YAML file `{}':".format(yaml_file)
    if pretty:
        # Pretty print
        pprint(list1)
        # Newline after pretty print
        print '\n'
    else:
        # Normal print
        print '{}\n'.format(list1)

    list1 = json_input(json_file)
    print "List read from JSON file `{}':".format(json_file)
    if pretty:
        # Pretty print
        pprint(list1)
    else:
        # Normal print
        print '{}\n'.format(list1)

if __name__ == '__main__':
    ppfiles(YAML_FILE, JSON_FILE)

