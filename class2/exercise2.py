#!/usr/bin/env python
####################################################################################################
'''
Using telnetlib, connect to a router, execute show ip interface brief, return the output
'''

# Imports
import argparse
import os
import socket
import sys
import telnetlib
import time
import yaml

# Globals
LOGIN_PROMPT = 'sername:'
PASSWORD_PROMPT = 'assword:'
ROUTER_CMD = 'show ip interface brief'
ROUTER_FILE = 'router.yaml'
ROUTER_NOPAGING = 'terminal length 0'
ROUTER_PROMPT = r'>|#'
TELNET_PORT = 23
TELNET_TIMEOUT = 5

__version__ = '0.0.1'


def yaml_input(file1):
    if os.path.isfile(file1):
        with open(file1) as f1:
            data1 = yaml.load(f1)
        return data1
    else:
        sys.exit('Invalid filename {}'.format(file1))

####################################################################################################
def node_login(router_auth, telnet_port, telnet_timeout, verbose=False):
    try:
        if verbose:
            print 'Trying {}...'.format(router_auth['ADDRESS'])
        node_conn = telnetlib.Telnet(router_auth['ADDRESS'], telnet_port, telnet_timeout)
    except socket.timeout as e:
        sys.exit('Connection to {} timed out'.format(router_auth['ADDRESS']))

    output = node_conn.read_until(LOGIN_PROMPT, telnet_timeout)
    if verbose:
        print 'Node authentication banner:\n{}'.format(output)
        print 'Logging in as {}...'.format(router_auth['USERNAME'])
    node_conn.write(router_auth['USERNAME'] + '\n')
    output = node_conn.read_until(PASSWORD_PROMPT, telnet_timeout)
    if verbose:
        # Skip first line, node echoing back username
        secondline = output.find('\n') + 1
        print 'Node password prompt:\n{}'.format(output[secondline:])
        print 'Submitting password...'
    node_conn.write(router_auth['PASSWORD'] + '\n')

    post_login_prompt = [LOGIN_PROMPT, ROUTER_PROMPT]
    if verbose:
        print 'Checking for successful login...'
    post_login_index, post_login_match, post_login_output = node_conn.expect(post_login_prompt,
            telnet_timeout*2)
    if verbose:
        print 'Post login output:\n{}'.format(post_login_output)
    if post_login_index == 0:
        sys.exit('Authentication failed')
    else:
        if verbose:
            print 'Authentication succeeded'

    return node_conn

def node_nopaging(node_conn, telnet_timeout, verbose=False):
    if verbose:
        print 'Disabling paging on node...'
    node_conn.write(ROUTER_NOPAGING + '\n')
    post_cmd_prompt = [ROUTER_PROMPT]
    post_cmd_index, post_cmd_match, post_cmd_output = node_conn.expect(post_cmd_prompt,
            telnet_timeout)
    if verbose:
        print 'Node output:\n{}'.format(post_cmd_output)

def node_cmd(node_conn, cmd, telnet_timeout, verbose=False):
    if verbose:
        print 'Sending command {}...'.format(cmd)
    node_conn.write(cmd + '\n')
    post_cmd_prompt = ['\n']
    # Read until newline sent back - this should be the node echoing back the command
    post_cmd_index, post_cmd_match, post_cmd_output = node_conn.expect(post_cmd_prompt,
            telnet_timeout)
    if verbose:
        print 'Node echoes back:  {}'.format(post_cmd_output)
    post_cmd_prompt = [ROUTER_PROMPT]
    # Read until node prompt, this should indicate command output is done
    post_cmd_index, post_cmd_match, post_cmd_output = node_conn.expect(post_cmd_prompt,
            telnet_timeout)
    # Strip off last line - node prompt
    lastline = post_cmd_output.rfind('\n')
    cmd_output = post_cmd_output[:lastline]
    if verbose:
        print 'Node output:\n{}'.format(post_cmd_output)

    return cmd_output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connect to a specified router and run a '
            'command')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
            default=False)
    parser.add_argument('-f', '--file', help='specify YAML file to read router info from',
            default=ROUTER_FILE)
    args = parser.parse_args()

    router_auth = yaml_input(args.file)
    node_conn = node_login(router_auth, TELNET_PORT, TELNET_TIMEOUT, args.verbose)
    node_nopaging(node_conn, TELNET_TIMEOUT, args.verbose)
    output = node_cmd(node_conn, ROUTER_CMD, TELNET_TIMEOUT, args.verbose)

    print 'Command output:\n{}'.format(output)

