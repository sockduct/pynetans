#!/usr/bin/env python
####################################################################################################
'''Script that:
 * Tests out argparse options
'''

# Standard Imports
import argparse
import sys

# Globals
OUTPUT_FILE = 'routers.pkl'
#OUTPUT_FILE_BASE = 'routers'
POLL_INTERVAL = 300  # How many seconds between each polling attempt
ROUTER_FILE = 'routers.yaml'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'April 27, 2016'
__version__ = '0.0.1'


def main(args):
    '''Acquire necessary input options, retrieve SNMP info, and... ???
    '''
    parser = argparse.ArgumentParser(
        description='Poll specified router(s) to detect configuration changes')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='display verbose output')
    parser.add_argument('-f', '--file', help='specify YAML file to read router info from',
        default=ROUTER_FILE)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--realtime', action='store_true',
        help='run forever and keep polling every {} seconds (default)'.format(POLL_INTERVAL),
        default=True)
    group.add_argument('-o', '--output', action='store_true', help='poll once and display results')
    parser.add_argument('-w', '--write', help='specify file to write results to')
    args = parser.parse_args()

    print 'args:  {}'.format(args)
    # Yields attribute error when printing:
    #print 'args.version:  {}'.format(args.version)
    print 'args.verbose:  {}'.format(args.verbose)
    print 'args.file:  {}'.format(args.file)
    print 'args.realtime:  {}'.format(args.realtime)
    print 'args.output:  {}'.format(args.output)
    print 'args.write:  {}'.format(args.write)
    if args.output:
        print 'args.output yielded true...'
    else:
        print 'default to args.realtime...'

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)

