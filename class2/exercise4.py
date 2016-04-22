#!/usr/bin/env python
####################################################################################################
'''Connect to routers pynet-rtr1 and pynet-rtr2.  For each router, retrieve the MIB2 sysName and
sysDescr OIDs and print them out.
'''

# Primary Imports
# Delete unused lines/comments!
import argparse
import os
import sys
import yaml

# 3rd Party Imports
from snmp_helper import snmp_get_oid, snmp_extract

# Globals
ROUTER_FILE = 'routers.yaml'
# sysName, sysDescr
SNMP_OIDs = [{'id': '1.3.6.1.2.1.1.5.0', 'obj': 'sysName'},
             {'id': '1.3.6.1.2.1.1.1.0', 'obj': 'sysDescr'}]

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<period>r<period>small<at>outlook<period>com'
__date__ = 'April 19, 2016'
__version__ = '0.0.1'


def yaml_input(file1):
    '''Read in router/switch authentication information from YAML file.'''
    if os.path.isfile(file1):
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
        return data1
    else:
        sys.exit('Invalid filename {}'.format(file1))

def snmp_query(node_info, oid):
    '''Query for OID on node - all necessary parameters should be part of node_info data
    structure
    '''
    snmp_output = snmp_get_oid(node_info, oid)
    output = snmp_extract(snmp_output)

    return output

####################################################################################################
def main(args):
    '''Acquire necessary input options and process SNMP node connection, authentication,  command
    execution and returning output.
    '''

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Connect to specified routers and run specified SNMP queries')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='display verbose output', default=False)
    parser.add_argument(
        '-f', '--file', help='specify YAML file to read router info from', default=ROUTER_FILE)
    args = parser.parse_args()

    # Populate router data structures list
    myrouters = yaml_input(args.file)

    for router in myrouters:
        snmp_info = (router['ADDRESS'], router['SNMP_COMMUNITY'], router['SNMP_PORT'])
        print '{} [{}:{}]:'.format(router['HOSTNAME'], router['ADDRESS'],
                                   router['SNMP_PORT'])
        for tgt_oid_info in SNMP_OIDs:
            result = snmp_query(snmp_info, tgt_oid_info['id'])
            print '{} ({}) ='.format(tgt_oid_info['obj'], tgt_oid_info['id']),
            if len(result) > 79:
                print ''
            print '{}'.format(result)
        print ''

# Call main and put all logic there per best practices.
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)

