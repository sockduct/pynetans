#!/usr/bin/env python
####################################################################################################
'''Use netmiko to send command show arp to multiple routers.'''

# Imports
import argparse
import datetime
from getpass import getpass
import netmiko
import os
import sys
import threading
import Queue
import yaml

# Globals
READ_BUF = 5000
ROUTER_FILE = 'routers-nm.yaml'
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

def rcmd(routerx, cmd, outq):
    '''Execute passed command on remote router and return result in passed queue'''
    try:
        router_conn = netmiko.ConnectHandler(**routerx)
        output = None
        success = True
    except netmiko.ssh_exception.NetMikoTimeoutException:
        output = 'Error:  Connection to {}:{} timed out...\n'.format(routerx['ip'],
                 routerx['port'])
        success = False
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        output = 'Error:  Authentication to {}:{} failed - check username/password\n'.format(
                 routerx['ip'], routerx['port'])
        success = False

    if not output:
        cmd_out = router_conn.send_command(cmd)
        output = '{} on [{}:{}]:\n{}\n'.format(cmd, routerx['ip'], routerx['port'], cmd_out)
        router_conn.disconnect()

    outq.put((success, output))


####################################################################################################
def main(args):
    '''Acquire necessary input options, execute show arp on multiple routers,
    process per CLI args.'''
    # Benchmark
    prog_start = datetime.datetime.now()
    print 'Program start time:  {}\n'.format(prog_start)

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
    parser.add_argument('-w', '--wait', action='store_true',
                        help="don't display results until all routers processed", default=False)
    args = parser.parse_args()

    # Initialize data structures
    myrouters = yaml_input(args.datafile, args.verbose)
    for router in myrouters:
        check_input(router, args.port, args.verbose)
    cmd = 'show arp'
    resultq = Queue.Queue()
    workers = []

    for router in myrouters:
        worker = threading.Thread(target=rcmd, args=(router, cmd, resultq))
        workers.append(worker)
        worker.start()

    # Believe preferable to print results as they are available versus waiting for everyone, so
    # this is default behavior which can be overridden by -w
    if args.wait:
        for worker in workers:
            worker.join()

        worked = 'Succeeded:\n'
        failed = 'Failed:\n'
        for worker in workers:
            status, result = resultq.get()
            if status:
                worked += result + '\n'
            else:
                failed += result
        print '{}\n{}'.format(worked, failed)
    else:
        for worker in workers:
            status, result = resultq.get()
            if not status:
                print 'Failed -',
            print result

    # Benchmark
    prog_end = datetime.datetime.now()
    print 'Program start time:  {}'.format(prog_end)
    prog_time = prog_end - prog_start
    print 'Ellapsed time:  {}'.format(prog_time)


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

