#!/usr/bin/env python
####################################################################################################
'''Use netmiko to enter into configuration mode and verify it worked on pynet-rtr2.'''

# Imports
import argparse
from getpass import getpass
import netmiko
import os
import socket
import sys
import time
import yaml

# Globals
READ_BUF = 5000
ROUTER_FILE = 'router-nm.yaml'
TIMEOUT = 5

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'May 7, 2016'
__version__ = '0.0.1'


####################################################################################################
def yaml_input(file1, verbose=False):
    '''Read in router/switch authentication information from YAML file.'''
    data1 = {}

    if os.path.isfile(file1):
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
    else:
        # Don't output error if using default file name
        if verbose and file1 != ROUTER_FILE:
            print 'Error:  Invalid filename {}'.format(file1)

    return data1

def check_input(router1, ssh_port, verbose=False):
    '''Validate router input data, prompt for anything missing.'''
    if 'device_type' not in router1:
        router1['device_type'] = raw_input('Router device type: ')
    if 'ip' not in router1:
        router1['ip'] = raw_input('Router IPv4 Address: ')
    if 'username' not in router1:
        router1['username'] = raw_input('Username for Router: ')
    if 'password' not in router1:
        router1['password'] = getpass()
    if 'port' not in router1:
        if verbose and not ssh_port:
            print 'Ssh port not specified, using default of 22.  Override with -p option.'
        if not ssh_port:
            ssh_port = 22
        router1['port'] = ssh_port
    elif ssh_port:
        if verbose:
            print 'overriding (ssh) port value ({}) with passed -p value ({})'.format(
                router1['port'], ssh_port)
        router1['port'] = ssh_port


####################################################################################################
def main(args):
    '''Acquire necessary input options, call to retrieve version info from router,
    process per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Retrieve show version output from specified router')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-d', '--datafile', help='specify YAML file to read router info from',
                        default=ROUTER_FILE)
    parser.add_argument('-p', '--port', help='specify ssh port (default is 22)')
    parser.add_argument('--prompt', action='store_true',
                        help='prompt for router info (do not try to read in from file)',
                        default=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
                        default=False)
    args = parser.parse_args()

    # Initialize data structures
    myrouter = yaml_input(args.datafile, args.verbose)
    check_input(myrouter, args.port, args.verbose)

    myrouter_conn = netmiko.ConnectHandler(**myrouter)
    myprompt = myrouter_conn.find_prompt()
    if args.verbose:
        print 'Entering router prompt:  {}'.format(myprompt)
    myrouter_conn.config_mode()
    myprompt = myrouter_conn.find_prompt()
    if args.verbose:
        print 'My router prompt after entering config mode:  {}'.format(myprompt)
    status = myrouter_conn.check_config_mode()
    if status:
        print 'My router is in configuration mode.'
    else:
        print 'My router is not in configuration mode.'
    myrouter_conn.exit_config_mode()

    myrouter_conn.disconnect()


# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    main(sys.argv[1:])


####################################################################################################
# Post coding
#
# pylint <script>.py
#   Score should be >= 8.0
#
# Future:
# * Testing - doctest/unittest/other
# * Logging
#

