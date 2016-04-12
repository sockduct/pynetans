#!/usr/bin/env python
####################################################################################################
'''
Simple program which takes a moderately involved Python list and outputs it in YAML and JSON
format
'''

# Imports
import argparse
import json
import yaml

# For reading from files
import exercise7

# Globals
BASE_FILE = 'exercise6'
YAML_FILE = BASE_FILE + '.yaml'
YAML_BOF = '---\n'
JSON_FILE = BASE_FILE + '.json'

__version__ = '0.0.1'


def yaml_output(list1, abroutform=True):
    with open(YAML_FILE, 'w') as f1:
        f1.write(YAML_BOF)
        f1.write(yaml.dump(list1, default_flow_style=abroutform))

def json_output(list1):
    with open(JSON_FILE, 'w') as f1:
        json.dump(list1, f1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output Python list into YAML and JSON'
            'formatted files')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output')
    args = parser.parse_args()

    list1 = [1, 2, 3, 'one', 'two', 'three', {'a': 'apple', 'b': 'banana', 'c': 'clementine'}]

    yaml_output(list1, False)
    json_output(list1)

    if args.verbose:
        print 'Example list:\n{}'.format(list1)
        print "\nList written to YAML formatted file `{}' and JSON formatted file `{}'.\n".format(
                YAML_FILE, JSON_FILE)
        exercise7.ppfiles(YAML_FILE, JSON_FILE)

