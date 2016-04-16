#!/usr/bin/env python
####################################################################################################
'''
Simple program which parses a Cisco IOS config file for crypto maps which don't use AES encryption;
for each of these crypto maps it then determines the transform set name, finds this transform set
configuration and outputs it along with the crypto map
'''

# Imports
from ciscoconfparse import CiscoConfParse
import re

# Globals
P_PARSE_STRING = 'crypto map CRYPTO'
C_PARSE_STRING = 'transform-set AES'
CISCO_IOS_FILE = 'cisco_ipsec.txt'

__version__ = '0.0.1'


def parse_conf_file_ts(cfg1, ts_line):
    ts = re.findall(r'[\w-]+', ts_line)[2]
    target = cfg1.find_objects(r'^\w.*transform-set ' + ts + r'\s')
    return target

def parse_conf_file_cm(file1):
    cisco_conf = CiscoConfParse(file1)
    target = cisco_conf.find_objects_wo_child(parentspec=r'^' + P_PARSE_STRING,
            childspec=C_PARSE_STRING)
    for p_elmt in target:
        print 'Found target:\n{}'.format(p_elmt.text)
        for c_elmt in p_elmt.all_children:
            print c_elmt.text
            if c_elmt.text.find('set transform-set') >= 0:
                target_ts = parse_conf_file_ts(cisco_conf, c_elmt.text)
        target_ts_parent = target_ts[0]
        print '\n{}'.format(target_ts_parent.text)
        for c_elmt in target_ts_parent.all_children:
            print c_elmt.text
        print ''

if __name__ == '__main__':
    parse_conf_file_cm(CISCO_IOS_FILE)

