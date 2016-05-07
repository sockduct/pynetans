#!/usr/bin/env python
####################################################################################################
'''Use paramiko to retrieve show version output from pynet-rtr2.'''

# Imports
import argparse
from getpass import getpass
import os
import paramiko
import socket
import sys
import time
import yaml

# Globals
READ_BUF = 5000
ROUTER_FILE = 'router.yaml'
SLEEP_DELAY = 0.5
TIMEOUT = 5
YAML_BOF = '---\n'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'May 7, 2016'
__version__ = '0.0.1'


####################################################################################################
class Router(object):
    '''A class to represent a Cisco router'''

    def __init__(self, ip_addr, username, password, port=22, verbose=False):
        self.ip_addr = ip_addr
        self.port = int(port)
        self.username = username
        self.password = password
        self.preconn = paramiko.SSHClient()
        # Insecure, but sufficient for lab use
        self.preconn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conn = None
        self.verbose = verbose

    def ssh_conn(self):
        '''Establish ssh connection.'''
        try:
            self.preconn.connect(self.ip_addr, username=self.username, password=self.password,
                                 look_for_keys=False, allow_agent=False, port=self.port,
                                 timeout=TIMEOUT)
            self.conn = self.preconn.invoke_shell()
            # Need to provide some time to receive all output
            time.sleep(SLEEP_DELAY)
            output = self.conn.recv(READ_BUF)
            if self.verbose:
                print 'Connected to {}:{}'.format(self.ip_addr, self.port)
                print 'Received:\n{}'.format(output)
        except socket.timeout:
            sys.exit('Error:  Connection to {} timed-out'.format(self.ip_addr))
        except paramiko.ssh_exception.AuthenticationException:
            sys.exit('Error:  Authentication to {} failed - check username/password'.format(
                    self.ip_addr))

    def ssh_close(self):
        '''Close ssh connection.'''
        self.conn.close()

    def no_paging(self, paging_cmd='terminal length 0'):
        '''Disable the paging of output. (i.e., --More--)'''
        return self.send_cmd(paging_cmd)

    def send_cmd(self, cmd):
        '''Send a command to connected device and return response.'''
        cmd = cmd.rstrip()
        if self.verbose:
            print 'Sending command {}...'.format(cmd)
        self.conn.send(cmd + '\n')
        # Need to provide some time to receive all output
        time.sleep(SLEEP_DELAY)
        return self.conn.recv(READ_BUF)


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
    if 'ADDRESS' not in router1:
        router1['ADDRESS'] = raw_input('Router IPv4 Address: ')
    if 'HOSTNAME' not in router1:
        router1['HOSTNAME'] = router1['ADDRESS']
    if 'USERNAME' not in router1:
        router1['USERNAME'] = raw_input('Username for Router: ')
    if 'PASSWORD' not in router1:
        router1['PASSWORD'] = getpass()
    if 'SSH_PORT' not in router1:
        if verbose and not ssh_port:
            print 'SSH_PORT not specified, using default of 22.  Override with -p option.'
        if not ssh_port:
            ssh_port = 22
        router1['SSH_PORT'] = ssh_port
    elif ssh_port:
        if verbose:
            print 'overriding SSH_PORT value ({}) with passed -p value ({})'.format(
                    router1['SSH_PORT'], ssh_port)
        router1['SSH_PORT'] = ssh_port



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

    if args.verbose:
        print 'Target router:  {}'.format(myrouter['HOSTNAME'])

    myrouter_conn = Router(myrouter['ADDRESS'], myrouter['USERNAME'], myrouter['PASSWORD'],
                           myrouter['SSH_PORT'], args.verbose)
    myrouter_conn.ssh_conn()
    myrouter_conn.no_paging()
    output = myrouter_conn.send_cmd('show version')
    if args.verbose:
        print 'Command output from {}:'.format(myrouter['HOSTNAME'])
    print output
    myrouter_conn.ssh_close()

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

