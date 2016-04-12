#!/usr/bin/env python
####################################################################################################
'''
Simple program which parses a Cisco IOS config file for crypto maps which don't use AES encryption
and outputs them
'''

# Imports
from ciscoconfparse import CiscoConfParse

# Globals
P_PARSE_STRING = 'crypto map CRYPTO'
C_PARSE_STRING = 'transform-set AES'
CISCO_IOS_FILE = 'cisco_ipsec.txt'

__version__ = '0.0.1'


def parse_conf_file(file1):
    cisco_conf = CiscoConfParse(file1)
    target = cisco_conf.find_objects_wo_child(parentspec=r'^' + P_PARSE_STRING,
            childspec=C_PARSE_STRING)
    for p_elmt in target:
        print 'Found target:\n{}'.format(p_elmt.text)
        for c_elmt in p_elmt.all_children:
            print c_elmt.text
        print ''

if __name__ == '__main__':
    parse_conf_file(CISCO_IOS_FILE)

