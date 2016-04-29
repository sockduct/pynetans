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
import json
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
#OUTPUT_FILE = ''  # Use default of empty string for stdout, allow user to specify file from CLI
#OUTPUT_FILE = 'routers.pkl'  # Decided better to just read from CLI
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
YAML_BOF = '---\n'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'April 23, 2016'
__version__ = '0.0.4'


def yaml_input(file1):
    '''Read in router/switch authentication information from YAML file.'''
    if os.path.isfile(file1):
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
        return data1
    else:
        sys.exit('Invalid filename {}'.format(file1))

def read_data(infile, file_format, infile_format, verbose=False):
    '''Read in router data from specified file.  Support Python pickle format, yaml format or
    json format and return data structure.'''
    if infile_format:
        read_format = infile_format
    else
        read_format = file_format

    if verbose:
        print 'Reading in previous output as {} formatted data from {}...'.format(read_format,
            infile)
    with open(infile, 'rb') as file1:
        if read_format == 'native':
            router_cfg_times = pickle.load(file1)
        elif read_format == 'yaml':
            router_cfg_times = yaml.load(file1)
        elif read_format == 'json':
            router_cfg_times = json.load(file1)
        else:
            sys.exit('Unsupported file format {}.'.format(read_format)
    if verbose:
        print 'Working data set now:\n{}'.format(router_cfg_times)

    return router_cfg_times

def write_data(outfile, file_format, outfile_format, yaml_format=True, verbose=False):
    '''Write router data from specified file.  Support Python pickle format, yaml format or
    json format and return data structure.'''
    if outfile_format:
        write_format = outfile_format
    else
        write_format = file_format

    if verbose:
        print 'Writing output as {} formatted data to {}...'.format(write_format, outfile)
    with open(outfile, 'wb') as file1:
        if write_format == 'native':
            pickle.dump(router_cfg_times, file1)
        elif write_format == 'yaml':
            file1.write(YAML_BOF)
            file1.write(yaml.dump(router_cfg_times, default_flow_style=yaml_format)
        elif write_format == 'json':
            json.dump(router_cfg_times, file1)
        else:
            sys.exit('Unsupported file format {}.'.format(write_format)

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

def poll_device(routers, router_cfg_times, verbose=False, quiet=False):
    '''Poll router(s) for specified data.'''
    for router in routers:
        # Start time of poll sequence for router
        now = datetime.datetime.today()
        router_config_changed = False
        change_output = ''
        if not quiet:
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
            if not quiet:
                if os.name == 'posix':
                    termcolor.cprint(message, 'yellow', attrs=['blink'])
                else:
                    # termcolor doesn't work on Windows, at least not from PowerShell
                    print message
                print 'Sending notification to {}'.format(RECIPIENT)
            subject_add = ' on {}'.format(router['HOSTNAME'])
            send_mail(RECIPIENT, SUBJECT+subject_add, message, SENDER)
        else:
            if not quiet:
                print 'No changes detected on {}.'.format(router['HOSTNAME'])
        if not quiet:
            print ''

    return router_cfg_times

####################################################################################################
def main(args):
    '''Acquire necessary input options, call to retrieve SNMP info, process per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Poll specified router(s) to detect configuration changes')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-d', '--datafile', help='specify YAML file to read router info from',
        default=ROUTER_FILE)
    parser.add_argument('-r', '--read',
        help='specify output file to load (from previous run of program - default is to start ' + \
            'from scratch)')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
        default=False)
    group1.add_argument('-q', '--quiet', action='store_true',
        help="don't display output (requires -w)", default=False)
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-c', '--continuous', action='store_true',
        help='run forever and keep polling every {} seconds (default)'.format(POLL_INTERVAL),
        default=True)
    group2.add_argument('-o', '--once', action='store_true',
        help='poll once and display results', default=False)
    parser.add_argument('-w', '--write', help='specify file to write results to (implies -o)')
    parser.add_argument('-f', '--format', help='specify input/output file format - native ' + \
        '(Python pickle - default if not specified) | yaml | json', default='native')
    parser.add_argument('--informat', help='specify input file format - native ' + \
        '(Python pickle) | yaml | json - (takes precedence over -f)')
    parser.add_argument('--outformat', help='specify output file format - native ' + \
        '(Python pickle) | yaml | json - (takes precedence over -f)')
    args = parser.parse_args()

    # Sanity checks
    if args.quiet and not args.write:
        sys.exit('Error:  quiet option specified without output file (-w)')
    elif args.write and not args.once:
        print 'Notice:  {} specified as output file - assuming once option '.format(args.write) + \
            '(use -ow {} to avoid this message)'.format(args.write, args.write)
        args.once = True

    myrouters = yaml_input(args.datafile)
    # Working data structure
    myrouter_cfg_times = {}
    if args.read:
        myrouter_cfg_times = read_data(args.read, args.format, args.informat, args.verbose)
    if args.once:
        if args.verbose:
            print 'Poll once and display results selected.'
        myrouter_cfg_times = poll_device(myrouters, myrouter_cfg_times, args.verbose, args.quiet)
        if args.write:
            write_data(args.write, args.format, args.outformat, verbose=args.verbose):
        elif args.verbose:
            print 'No output file specified - not saving data set.'
    # args.continuous == True implied
    else:
        if args.verbose:
            print 'Real-time monitoring selected.'
        # Keep polling every POLL_INTERVAL forever
        while True:
            myrouter_cfg_times = poll_device(myrouters, myrouter_cfg_times, args.verbose,
                args.quiet)
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


# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)


####################################################################################################
#
# To do:
# * Test new read/write formats
# * Need option to allow inputting router data from CLI or prompting for it
# * Need option to output YAML template for router data
# * Need option to prompt for missing data from YAML input file
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
