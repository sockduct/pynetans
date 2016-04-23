#!/usr/bin/env python
####################################################################################################
'''Script that:
 * Uses SNMPv3 to monitor router(s) for configuration changes
 * If a configuration change occurs, provide E-mail notification and specify on which router(s)
   the configuration changed
'''

# Standard Imports
import argparse
from collections import OrderedDict
import datetime
import os
import pickle
import sys
import yaml

# Local Imports
import email_helper
import snmp_helper

# Globals
ROUTER_FILE = 'routers.yaml'
SNMP_TARGETS = OrderedDict([('ccmHistoryRunningLastChanged', '1.3.6.1.4.1.9.9.43.1.1.1.0'),
                ('ccmHistoryRunningLastSaved', '1.3.6.1.4.1.9.9.43.1.1.2.0'),
                ('ccmHistoryStartupLastChanged', '1.3.6.1.4.1.9.9.43.1.1.3.0')])
WORKING_FILE = 'exercise1.data'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'April 23, 2016'
__version__ = '0.0.1'


#class Myclass1(object):
    #'''<description>'''

    #__init__(self, param1):
    #    '''<description>'''
    #    self.param1 = param1

    #method1(self, param1):
    #    '''<description>'''
    #    pass

def yaml_input(file1):
    '''Read in router/switch authentication information from YAML file.'''
    if os.path.isfile(file1):
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
        return data1
    else:
        sys.exit('Invalid filename {}'.format(file1))

def timeticks_to_datetime(ticks):
    '''Convert SNMP timeticks (1/100 of second) to datetime value'''
    seconds = int(ticks)/100
    return str(datetime.timedelta(seconds=seconds))

####################################################################################################
def get_snmp_data(snmp_device, snmp_auth, oid):
    '''Retrieve SNMPv3 data, extract and return'''
    result = snmp_helper.snmp_get_oid_v3(snmp_device, snmp_auth, oid)
    data = snmp_helper.snmp_extract(result)
    return data

def main(args):
    '''Acquire necessary input options, retrieve SNMP info, and... ???
    '''
    parser = argparse.ArgumentParser(
        description='Connect to a specified router and run a command')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='display verbose output', default=False)
    parser.add_argument(
        '-f', '--file', help='specify YAML file to read router info from', default=ROUTER_FILE)
    args = parser.parse_args()

    myrouters = yaml_input(args.file)
    #
    #print 'SNMP_TARGETS = {}'.format(SNMP_TARGETS)
    #for t in SNMP_TARGETS:
    #    print '{} = {}'.format(t, SNMP_TARGETS[t])
    #sys.exit()
    #
    for router in myrouters:
        # Start time of poll sequence for router
        now = datetime.datetime.today()
        print 'Router {} - Poll start time {}:'.format(router['HOSTNAME'], now)
        for snmp_target in SNMP_TARGETS:
            snmp_result = get_snmp_data((router['ADDRESS'], router['SNMP_PORT']),
                              (router['SNMP_USER'], router['SNMP_AUTH'], router['SNMP_KEY']),
                              SNMP_TARGETS[snmp_target])
            # Output data
            snmp_result_formatted = timeticks_to_datetime(snmp_result)
            print '{} ({}):  {} ({})'.format(snmp_target, SNMP_TARGETS[snmp_target],
                                             snmp_result_formatted, snmp_result)
        print ''

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)


####################################################################################################
# Post coding
#
# pylint <script>.py
#   Score should be >= 8.0
#
# Planned:
# * Allow router info from CLI
# * Implement and test all CLI options
# * Add test cases with unittest or doctest
#
# Future:
# * Testing - doctest/unittest/other
# * Logging
#
