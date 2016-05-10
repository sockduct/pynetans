#!/usr/bin/env python
####################################################################################################
'''Use netmiko to change the logging buffer size and console logging on pynet-rtr1 and
pynet-rtr2.'''

# Imports
import argparse
from getpass import getpass
import netmiko
import os
import sys
import yaml

# Globals
CONFIG_FILE = 'exercise8.cmds'
READ_BUF = 5000
ROUTER_FILE = 'routers1-nm.yaml'
TIMEOUT = 5

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'May 9, 2016'
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
    '''Acquire necessary input options, call to run config commands on routers,
    process per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Change logging buffer size and disable console logging on specified routers')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-c', '--configfile',
                        help='specify file to read router configuration commands from',
                        default=CONFIG_FILE)
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
    if not args.prompt:
        myrouters = yaml_input(args.datafile, args.verbose)
        if myrouters == {}:
            myrouters = [{}]
    else:
        myrouters = [{}]
    # Check if myrouters is a list or a dictionary - expecting list of dictionaries, fix where
    # there is only a single dictionary present
    if isinstance(myrouters, dict):
        myrouters = [myrouters]
    elif not isinstance(myrouters, list):
        sys.exit('Error:  Invalid data structure read from {}'.format(args.datafile))
    for router in myrouters:
        check_input(router, args.port, args.verbose)

    for router in myrouters:
        try:
            router_conn = netmiko.ConnectHandler(**router)
        except netmiko.ssh_exception.NetMikoTimeoutException:
            sys.exit('Error:  Connection to {}:{} timed out...'.format(router['ip'],
                router['port']))
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            sys.exit('Error:  Authentication to {}:{} failed - check username/password'.format(
                router['ip'], router['port']))

        if args.verbose:
            output = router_conn.send_command('show run | inc logging')
            print 'Logging commands on {}:{} before change:\n{}\n'.format(router['ip'],
                router['port'], output)
        router_conn.config_mode()
        status = router_conn.check_config_mode()
        if status:
            router_conn.send_config_from_file(config_file=args.configfile)
        else:
            sys.exit('Error:  Failed to enter configuration mode.')
        router_conn.exit_config_mode()
        if args.verbose:
            output = router_conn.send_command('show run | inc logging')
            print 'Logging commands on {}:{} after change:\n{}\n'.format(router['ip'],
                router['port'], output)
        router_conn.disconnect()


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

