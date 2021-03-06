#!/usr/bin/env python
####################################################################################################
'''Simple program which takes a moderately involved Python list and outputs it in YAML format.'''

# Imports
import argparse
import yaml

# Globals
BASE_FILE = 'example'
YAML_FILE = BASE_FILE + '.yaml'
YAML_BOF = '---\n'

__version__ = '0.0.1'


def yaml_output(data1, abroutform=True):
    with open(YAML_FILE, 'w') as f1:
        f1.write(YAML_BOF)
        f1.write(yaml.dump(data1, default_flow_style=abroutform))

def ppfiles(yaml_file, json_file, pretty=True):
    data1 = yaml_input(yaml_file)
    print "List read from YAML file `{}':".format(yaml_file)
    if pretty:
        # Pretty print
        pprint(data1)
        # Newline after pretty print
        print '\n'
    else:
        # Normal print
        print '{}\n'.format(data1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output Python data structures into YAML '
            'formatted files')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output')
    args = parser.parse_args()

    router1 = {'ADDRESS': '1.2.3.4', 'SNMP_COMMUNITY': 'public1', 'SNMP_PORT': '161'}
    router2 = {'ADDRESS': '1.2.3.5', 'SNMP_COMMUNITY': 'public2', 'SNMP_PORT': '8161'}
    router_list = [router1, router2]

    yaml_output(router_list, False)

    if args.verbose:
        print 'Example list:\n{}'.format(data1)
        print "\nList written to YAML formatted file `{}'.\n".format(YAML_FILE)
        ppfiles(YAML_FILE)


