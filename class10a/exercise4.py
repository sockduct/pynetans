#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
'''Use the PyEZ load() method to set the hostname of the SRX using set, conf (curly brace), and
   XML formats.
'''

# Imports
import argparse
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import os
import sys
import yaml

# Globals
# Note:  Consider using function/class/method default parameters instead of global constants where
# it makes sense
#BASE_FILE = 'file1'
SRX_ORIG_HOSTNAME = 'pynet-jnpr-srx1'
SRX_NEW_HOSTNAME = 'mysrx1'
SRX_CONF_FILE = 'chg_hostname.cfg'
SRX_XML_FILE = 'chg_hostname.xml'
SRX_CONF_CHG1 = 'set system host-name {}'.format(SRX_NEW_HOSTNAME)
SRX_CONF_CHG2 = 'set system host-name {}'.format(SRX_ORIG_HOSTNAME)
SRX_FILE = 'srx1.yaml'
TIMEOUT = 60

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'June 25, 2016'
__version__ = '0.0.1'


####################################################################################################
def yaml_input(file1, verbose=False):
    '''Read in router/switch authentication information from YAML file.'''
    data1 = {}

    if os.path.isfile(file1):
        if verbose:
            print 'Reading data file ({})'.format(file1)
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
    else:
        # Don't output error if using default file name
        if verbose and file1 != SRX_FILE:
            print 'Error:  Invalid filename {}'.format(file1)

    return data1

def check_input(srx1, verbose=False):
    '''Validate router input data, prompt for anything missing.'''
    if 'HOST' not in srx1:
        srx1['HOST'] = raw_input('SRX IPv4 Address: ')
    if 'USER' not in srx1:
        srx1['USER'] = raw_input('Username for SRX: ')
    if 'PASSWORD' not in srx1:
        srx1['PASSWORD'] = getpass()

def srx_conf(srx1, srx1_cfg, cfg1, form1, merge1, commit1, commit_comment=None, verbose=False):
    '''Make configuration changes on SRX device.'''
    # Lock config
    if verbose:
        print 'Locking configuration of {}'.format(srx1['HOST'])
    srx1_cfg.lock()
    if verbose:
        print 'Changing configuration of {}'.format(srx1['HOST'])
    if form1 == 'set':
        srx1_cfg.load(cfg1, format=form1, merge=merge1)
    else:
        srx1_cfg.load(path=cfg1, format=form1, merge=merge1)
    print 'Difference between current and candidate configuration:\n{}'.format(srx1_cfg.diff())
    if verbose and commit1:
        print 'Committing configuration changes to {}'.format(srx1['HOST'])
    elif verbose:
        print 'Rolling back configuration changes to {}'.format(srx1['HOST'])
    if commit1:
        srx1_cfg.commit(comment=commit_comment)
    else:
        srx1_cfg.rollback(0)
    if verbose:
        print 'Unlocking configuration of {}'.format(srx1['HOST'])
    srx1_cfg.unlock()

####################################################################################################
def main(args):
    '''Acquire necessary input options, interact with SRX device as specified per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Interact with specified SRX device as specified')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-d', '--datafile', help='specify YAML file to read router info from',
                        default=SRX_FILE)
    parser.add_argument('--prompt', action='store_true',
                        help='prompt for router info (do not try to read in from file)',
                        default=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
                        default=False)
    args = parser.parse_args()
    # Debugging
    #if args.verbose:
    #    print 'Args = {}'.format(args)

    # Initialize data structures
    mysrx = {}
    if not args.prompt:
        mysrx = yaml_input(args.datafile, args.verbose)
        # Debugging
        #if args.verbose:
        #    print 'mysrx = {}'.format(mysrx)
    else:
        if args.verbose:
            print 'Prompting specified - asking user for all connection details'
    check_input(mysrx, args.verbose)

    mysrx_conn = Device(host=mysrx['HOST'], user=mysrx['USER'], password=mysrx['PASSWORD'])
    if args.verbose:
        print 'Opening NETCONF connection to {}...'.format(mysrx['HOST'])
    mysrx_conn.open()
    # Set timeout - default of 30 seconds can be problematic, must set after open()
    mysrx_conn.timeout = TIMEOUT

    mysrx_cfg = Config(mysrx_conn)
    # Change 1
    if args.verbose:
        print '\nChange #1'
    srx_conf(mysrx, mysrx_cfg, SRX_CONF_CHG1, 'set', True, False, verbose=args.verbose)

    # Change 2
    if args.verbose:
        print '\nChange #2'
    srx_conf(mysrx, mysrx_cfg, SRX_CONF_FILE, 'text', True, True,
             'Temporarily changing hostname.', args.verbose)

    # Change 3
    if args.verbose:
        print '\nChange #3'
    srx_conf(mysrx, mysrx_cfg, SRX_XML_FILE, 'xml', True, True,
             'Restoring original hostname.', args.verbose)

    # Cleanup
    mysrx_conn.close()

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    # Recommended by Matt Harrison in Beginning Python Programming
    # sys.exit(main(sys.argv[1:]) or 0)
    # Simplied version recommended by Kirk Byers
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

