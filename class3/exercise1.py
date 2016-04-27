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
import termcolor
import time
import yaml

# Local Imports
from email_helper import send_mail
import snmp_helper

# Globals
CONFIG_CHANGES = {'ccmHistoryRunningLastChanged': 'running-config changed',
                  'ccmHistoryRunningLastSaved': 'running-config saved',
                  'ccmHistoryStartupLastChanged': 'startup-config changed'}
OUTPUT_FILE = 'routers.pkl'
#OUTPUT_FILE_BASE = 'routers'
POLL_INTERVAL = 300  # How many seconds between each polling attempt
RECIPIENT = 'jsmall@localhost'
ROUTER_FILE = 'routers.yaml'
SENDER = 'class3.exercise1@localhost'
SNMP_MARK = 'sysUpTime'  # Offset from this used to measure change time
SNMP_TARGETS = OrderedDict([('sysUpTime', '1.3.6.1.2.1.1.3.0'),
                            ('ccmHistoryRunningLastChanged', '1.3.6.1.4.1.9.9.43.1.1.1.0'),
                            ('ccmHistoryRunningLastSaved', '1.3.6.1.4.1.9.9.43.1.1.2.0'),
                            ('ccmHistoryStartupLastChanged', '1.3.6.1.4.1.9.9.43.1.1.3.0')])
#SNMP_TRACK = 'ccmHistory'  # Only track changes in SNMP TARGETS starting with this prefix
SNMP_TRACK = 'ccmHistoryRunning'  # Only track changes in SNMP TARGETS starting with this prefix
SUBJECT = 'Alert - router configuration change'
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

def poll_device(routers, router_cfg_times, verbose=False):
    '''Poll router(s) for specified data.'''
    # Working data structure
    router_cfg_times = {}

    for router in routers:
        # Start time of poll sequence for router
        now = datetime.datetime.today()
        router_config_changed = False
        change_output = ''
        print 'Router {} - Poll start time {}:'.format(router['HOSTNAME'], now)
        if router['HOSTNAME'] not in router_cfg_times:
            router_cfg_times[router['HOSTNAME']] = OrderedDict([('LAST_POLLTIME', now),
                                                                ('CHECK_TIMES', False)])
        else:
            router_cfg_times[router['HOSTNAME']]['LAST_POLLTIME'] = now
            router_cfg_times[router['HOSTNAME']]['CHECK_TIMES'] = True
        for snmp_target in SNMP_TARGETS:
            snmp_result = get_snmp_data((router['ADDRESS'], router['SNMP_PORT']),
                              (router['SNMP_USER'], router['SNMP_AUTH'], router['SNMP_KEY']),
                              SNMP_TARGETS[snmp_target])
            # If check_times then need to compare new and old...
            if router_cfg_times[router['HOSTNAME']]['CHECK_TIMES']:
                # Only track changes that start with SNMP_TRACK
                if SNMP_TRACK in snmp_target:
                    if router_cfg_times[router['HOSTNAME']][snmp_target] < snmp_result:
                        router_config_changed = True
                        router_cfg_times[router['HOSTNAME']][snmp_target+'_CHANGED'] = True
                        diff_uptime = int(
                            router_cfg_times[router['HOSTNAME']][SNMP_MARK]) - int(snmp_result)
                        # diff_uptime is in ticks, convert to seconds
                        systime = time.time() - (diff_uptime/100)
                        systimestr = time.strftime("%a, %b %d %Y %H:%M:%S", time.localtime(
                            systime))
                        router_cfg_times[router['HOSTNAME']][snmp_target] = snmp_result
                        diff_datetime = timeticks_to_datetime(diff_uptime)
                        change_output += '{} ({}) changed {} ({}) ago\n'.format(
                            CONFIG_CHANGES[snmp_target], snmp_target, diff_datetime,
                            diff_uptime)
                        change_output += 'Change occurred at {} local system time'.format(
                            systimestr)
                    elif router_cfg_times[router['HOSTNAME']][snmp_target] > snmp_result:
                        sys.exit(
                            'Error: {} on {} decreased in value, something went wrong.'.format(
                            snmp_target, router['HOSTNAME']))
                    else:
                        router_cfg_times[router['HOSTNAME']][snmp_target+'_CHANGED'] = False
                else:
                    router_cfg_times[router['HOSTNAME']][snmp_target] = snmp_result
            else:
                router_cfg_times[router['HOSTNAME']][snmp_target] = snmp_result
            # Output data - should put this into a class with a print/string method
            if verbose:
                snmp_result_formatted = timeticks_to_datetime(snmp_result)
                print '{} ({}):  {} ({})'.format(snmp_target, SNMP_TARGETS[snmp_target],
                    snmp_result_formatted, router_cfg_times[router['HOSTNAME']][snmp_target])
        # Was there a config change in the router?
        if router_config_changed:
            message = '\nChanges detected on {}:\n{}'.format(router['HOSTNAME'],
                change_output)
            if os.name == 'posix':
                termcolor.cprint(message, 'yellow', attrs=['blink'])
            else:
                # termcolor doesn't work on Windows, at least not from PowerShell
                print message
            print 'Sending notification to {}'.format(RECIPIENT)
            subject_add = ' on {}'.format(router['HOSTNAME'])
            send_mail(RECIPIENT, SUBJECT+subject_add, message, SENDER)
        print ''

        return router_cfg_times

def main(args):
    '''Acquire necessary input options, retrieve SNMP info, and... ???
    '''
    parser = argparse.ArgumentParser(
        description='Poll specified router(s) to detect configuration changes')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='display verbose output', default=False)
    parser.add_argument('-f', '--file', help='specify YAML file to read router info from',
        default=ROUTER_FILE)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--realtime', action='store_true',
        help='run forever and keep polling every {} seconds (default)'.format(POLL_INTERVAL),
        default=True)
    group.add_argument('-o', '--output', help='specify file to write results to',
        default=OUTPUT_FILE)
    args = parser.parse_args()

    myrouters = yaml_input(args.file)
    myrouter_cfg_times = {}
    if args.realtime:
        # Keep polling every POLL_INTERVAL forever
        while True:
            myrouter_cfg_times = poll_device(myrouters, myrouter_cfg_times, args.verbose)
            if args.verbose:
                del_str = '\b' * 24
                count = POLL_INTERVAL
                while count > 0:
                    print '{}Sleeping for {:>6}...'.format(del_str, count),
                    # Doesn't display correctly in Linux without this:
                    sys.stdout.flush()
                    count -= 1
                    time.sleep(1)
                print '\n'
            else:
                print 'Sleeping for {}...\n'.format(POLL_INTERVAL),
                time.sleep(POLL_INTERVAL)
    else:
        myrouter_cfg_times = poll_device(myrouters, myrouter_cfg_times, args.verbose)
        with open(args.output, 'wb') as outfile:
            pickle.dump(myrouter_cfg_times, outfile)


# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)


####################################################################################################
#
# To do:
# * Need option to read in outputted pickle file
# * How to use default file name for output file?
# * Default realtime doesn't work right - if specify -o still does realtime...
#
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
