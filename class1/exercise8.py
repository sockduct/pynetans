#!/usr/bin/env python
####################################################################################################
'''
Simple program which parses a Cisco IOS config file for crypto maps and outputs them
'''

# Imports
from ciscoconfparse import CiscoConfParse

# Globals
PARSE_STRING = 'crypto map CRYPTO'
CISCO_IOS_FILE = 'cisco_ipsec.txt'

__version__ = '0.0.1'


def parse_conf_file(file1):
    cisco_conf = CiscoConfParse(file1)
    target = cisco_conf.find_objects(r'^' + PARSE_STRING)
    for p_elmt in target:
        print 'Found target:\n{}'.format(p_elmt.text)
        for c_elmt in p_elmt.all_children:
            print c_elmt.text
        print ''

if __name__ == '__main__':
    parse_conf_file(CISCO_IOS_FILE)

