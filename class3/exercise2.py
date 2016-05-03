#!/usr/bin/env python
####################################################################################################
'''Create two SVG image files based on SNMPv3 data

* 1st image file graphs I/O octets for pynet-rtr1/fa4 every 5 minutes for an hour
* 2nd image file graphs I/O unicast packets for same
'''

# Standard Imports
import argparse
from collections import OrderedDict
import datetime
import os
import pygal
import sys
import time
import yaml

# Local Imports
import snmp_helper

# Globals
DEL_STR = '\b' * 24
GRAPH1_OUT = 'graph1.svg'
GRAPH2_OUT = 'graph2.svg'
POLL_INTERVAL = 300  # How many seconds between each polling attempt
POLL_NUMBER = 12  # How many times to poll for data series?
ROUTER_FILE = 'router.yaml'
SNMP_TARGET_DESCR = ('ifDescr_fa4', '1.3.6.1.2.1.2.2.1.2.5')
SNMP_TARGETS = OrderedDict([('ifInOctets_fa4', '1.3.6.1.2.1.2.2.1.10.5'),
                            ('ifOutOctets_fa4', '1.3.6.1.2.1.2.2.1.16.5'),
                            ('ifInUcastPkts_fa4', '1.3.6.1.2.1.2.2.1.11.5'),
                            ('ifOutUcastPkts_fa4', '1.3.6.1.2.1.2.2.1.17.5')])
SNMP_TARGET_AXES = OrderedDict([('ifInOctets_fa4', 'Inbound'),
                                ('ifOutOctets_fa4', 'Outbound'),
                                ('ifInUcastPkts_fa4', 'Inbound'),
                                ('ifOutUcastPkts_fa4', 'Outbound')])
SNMP_TARGET_TITLE = OrderedDict([('ifInOctets_fa4', 'Inbound/Outbound Bytes for '),
                                 ('ifInUcastPkts_fa4', 'Inbound/Outbound Packets for ')])
YAML_BOF = '---\n'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'April 29, 2016'
__version__ = '0.0.3'


def yaml_input(file1):
    '''Read in router/switch authentication information from YAML file.'''
    if os.path.isfile(file1):
        with open(file1) as fh1:
            data1 = yaml.load(fh1)
        return data1
    else:
        sys.exit('Error:  Invalid filename {}'.format(file1))

####################################################################################################
def get_snmp_data(snmp_device, snmp_auth, oid):
    '''Retrieve SNMPv3 data, extract and return'''
    result = snmp_helper.snmp_get_oid_v3(snmp_device, snmp_auth, oid)
    data = snmp_helper.snmp_extract(result)
    return data

def poll_device(router, router_io_set, io_round, verbose=False, quiet=False):
    '''Poll router for specified data.'''
    # Start time of poll sequence for router
    now = str(datetime.datetime.today())
    router_io_set['LAST_POLLTIME'] = now
    if verbose:
        print '\nPoll start time {}, I/O Round -{}-:'.format(router_io_set['LAST_POLLTIME'],
            io_round)
    elif not quiet:
        print 'Polling...            ',
        # Doesn't display correctly in Linux without this:
        sys.stdout.flush()
    for snmp_target in SNMP_TARGETS:
        snmp_result = get_snmp_data((router['ADDRESS'], router['SNMP_PORT']),
                          (router['SNMP_USER'], router['SNMP_AUTH'], router['SNMP_KEY']),
                          SNMP_TARGETS[snmp_target])
        # If the first set
        if io_round == 0:
            # The indexed results above are a relative offset from this base value
            router_io_set[snmp_target] = []
            router_io_set[snmp_target].append(0)
            router_io_set[snmp_target+'-base_offset'] = snmp_result
        else:
            # Running tally is current value minus previous value
            router_io_set[snmp_target].append(int(snmp_result) -
                int(router_io_set[snmp_target][io_round-1]) -
                int(router_io_set[snmp_target+'-base_offset']))
        if verbose:
            print '{} = {}, relative offset from previous sample:  {}'.format(snmp_target,
                snmp_result, router_io_set[snmp_target][io_round])

    return router_io_set

def graph_data(ds1, ds2, title, x_axis, ds1_label, ds2_label, outfile, verbose=False, quiet=False):
    '''Graph data polled from router.'''
    line_chart = pygal.Line()

    if verbose:
        print '\nTitle = {}'.format(title)
        print 'X_Labels = {}'.format(x_axis)
        print 'Data Set 1 Label = {}'.format(ds1_label)
        print 'Data Set 1 = {}'.format(ds1)
        print 'Data Set 2 Label = {}'.format(ds2_label)
        print 'Data Set 2 = {}'.format(ds2)
    line_chart.title = title
    line_chart.x_labels = x_axis
    line_chart.add(ds1_label, ds1)
    line_chart.add(ds2_label, ds2)
    line_chart.render_to_file(outfile)
    if verbose:
        print 'Created SVG graphics file for data set:  {}'.format(outfile)
    elif not quiet:
        print DEL_STR*2,
        print 'Writing {}...          '.format(outfile),
        # Doesn't display correctly in Linux without this:
        sys.stdout.flush()

####################################################################################################
def main(args):
    '''Acquire necessary input options, call to retrieve SNMP info, process per CLI args.'''
    parser = argparse.ArgumentParser(
        description='Poll specified router(s) over a defined interval to graph interface I/O')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-d', '--datafile', help='specify YAML file to read router info from',
        default=ROUTER_FILE)
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
        default=False)
    group1.add_argument('-q', '--quiet', action='store_true',
        help="don't display output (requires -w)", default=False)
    args = parser.parse_args()

    # Initialize data structures
    myrouter = yaml_input(args.datafile)
    if args.verbose:
        print 'Target router:  {}'.format(myrouter['HOSTNAME'])
    myrouter_io_set = {}
    # Get interface description data
    snmp_result = get_snmp_data((myrouter['ADDRESS'], myrouter['SNMP_PORT']),
                    (myrouter['SNMP_USER'], myrouter['SNMP_AUTH'], myrouter['SNMP_KEY']),
                    SNMP_TARGET_DESCR[1])
    myrouter_io_set[SNMP_TARGET_DESCR[0]] = snmp_result
    if args.verbose:
        print 'Interface description for {} = {}'.format(SNMP_TARGET_DESCR[0],
            myrouter_io_set[SNMP_TARGET_DESCR[0]])
    # Collect POLL_NUMBER data sets, + 1 because 0 used for base_offset, want POLL_NUMBER data
    # sets after baseline
    for my_io_round in range(POLL_NUMBER+1):
        if my_io_round == 0:
            myrouter_io_set['x_axis'] = []
        else:
            myrouter_io_set['x_axis'].append(str(POLL_INTERVAL*my_io_round))
        myrouter_io_set = poll_device(myrouter, myrouter_io_set, my_io_round, args.verbose,
            args.quiet)
        count = POLL_INTERVAL
        while count > 0 and my_io_round < POLL_NUMBER:
            if not args.quiet:
                print '{}Sleeping for {:>6}...'.format(DEL_STR, count),
                # Doesn't display correctly in Linux without this:
                sys.stdout.flush()
            count -= 1
            time.sleep(1)
            if not args.quiet:
                print DEL_STR, '                      ', DEL_STR,
                # Doesn't display correctly in Linux without this:
                sys.stdout.flush()
    # Graph data set
    dataset1 = myrouter_io_set['ifInOctets_fa4'][1:]
    dataset2 = myrouter_io_set['ifOutOctets_fa4'][1:]
    dataset3 = myrouter_io_set['ifInUcastPkts_fa4'][1:]
    dataset4 = myrouter_io_set['ifOutUcastPkts_fa4'][1:]
    title1 = SNMP_TARGET_TITLE['ifInOctets_fa4'] + myrouter_io_set[SNMP_TARGET_DESCR[0]] + \
        ' on {}'.format(myrouter['HOSTNAME'])
    title2 = SNMP_TARGET_TITLE['ifInUcastPkts_fa4'] + myrouter_io_set[SNMP_TARGET_DESCR[0]] + \
        ' on {}'.format(myrouter['HOSTNAME'])
    graph_data(dataset1, dataset2, title1, myrouter_io_set['x_axis'],
        SNMP_TARGET_AXES['ifInOctets_fa4'], SNMP_TARGET_AXES['ifOutOctets_fa4'], GRAPH1_OUT,
        args.verbose, args.quiet)
    graph_data(dataset3, dataset4, title2, myrouter_io_set['x_axis'],
        SNMP_TARGET_AXES['ifInUcastPkts_fa4'], SNMP_TARGET_AXES['ifOutUcastPkts_fa4'], GRAPH2_OUT,
        args.verbose, args.quiet)
    if not args.quiet:
        print ''

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)


####################################################################################################
#
# To do:
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
