#!/usr/bin/env python
####################################################################################################
'''Use pexpect to change buffer logging size on pynet-rtr2.'''

# Imports
import argparse
from getpass import getpass
import os
import pexpect
import sys
import yaml

# Globals
PROMPT = '#'
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
        self.conn = None
        self.verbose = verbose

    def ssh_conn(self):
        '''Establish ssh connection.'''
        try:
            self.conn = pexpect.spawn('ssh -l {} {} -p {}'.format(self.username, self.ip_addr,
                                                                  self.port))
            self.conn.timeout = TIMEOUT
            # This will fail if the target's key fingerprint isn't locally cached
            self.conn.expect('assword:')
            self.conn.sendline(self.password)
            self.conn.expect(PROMPT)
            output = self.conn.before + self.conn.after
            if self.verbose:
                print 'Connected to {}:{}'.format(self.ip_addr, self.port)
                print 'Received:\n{}'.format(output)
        except pexpect.exceptions.TIMEOUT:
            sys.exit('Error:  Connection to {} timed-out or failed to authenticate'.format(
                self.ip_addr))

    def ssh_close(self, close_cmd='exit'):
        '''Close ssh connection.'''
        return self.send_cmd(close_cmd, r'onnection.*closed')

    def no_paging(self, paging_cmd='terminal length 0'):
        '''Disable the paging of output. (i.e., --More--)'''
        return self.send_cmd(paging_cmd)

    def send_cmd(self, cmd, result=PROMPT):
        '''Send a command to connected device and return response.'''
        cmd = cmd.rstrip()
        if self.verbose:
            print 'Sending command {}...'.format(cmd)
        self.conn.sendline(cmd)
        self.conn.expect(result)
        return self.conn.before + self.conn.after


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
    '''Acquire necessary input options, call to set logging buffer size on router,
    process per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Change logging buffer size on specified router and check')
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

    # Sanity check - pexpect spawn method not supported on Windows
    if os.name != 'posix':
        sys.exit('Error:  Only Posix systems (e.g., Linux) supported.')

    # Initialize data structures
    myrouter = yaml_input(args.datafile, args.verbose)
    check_input(myrouter, args.port, args.verbose)
    config_cmds = ['config terminal', 'logging buffered 32000', 'end']

    if args.verbose:
        print 'Target router:  {}'.format(myrouter['HOSTNAME'])

    myrouter_conn = Router(myrouter['ADDRESS'], myrouter['USERNAME'], myrouter['PASSWORD'],
                           myrouter['SSH_PORT'], args.verbose)
    myrouter_conn.ssh_conn()
    output = myrouter_conn.no_paging()
    if args.verbose:
        print output

    output = myrouter_conn.send_cmd('show run | inc logging.buffered')
    print 'Initial router logging buffer size:\n{}'.format(output)
    for cmd in config_cmds:
        output = myrouter_conn.send_cmd(cmd)
        if args.verbose:
            print 'Command output from {}:'.format(myrouter['HOSTNAME'])
            print output
    output = myrouter_conn.send_cmd('show run | inc logging.buffered')
    print 'Final router logging buffer size:\n{}'.format(output)

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

