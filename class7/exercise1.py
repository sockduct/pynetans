#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
'''Use Arista's eAPI/pyeapi to obtain 'show interfaces' from the switch.  Parse the
   'show interfaces' output to obtain the 'inOctets' and 'outOctets' fields for each
   of the interfaces on the switch.'''

# Imports
import pyeapi  # This uses ~/.eapi.conf for device and authentication information
import sys

# Globals
# Note:  Consider using function/class/method default parameters instead of global constants where
# it makes sense
#BASE_FILE = 'file1'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'May 21, 2016'
__version__ = '0.0.1'


def main(args):
    '''Connect to Arista switch and retrieve info'''
    pynet_sw4 = pyeapi.connect_to('pynet-sw4')
    output = pynet_sw4.enable('show interfaces')
    # Unpack from list
    output = output[0]
    # Only interested in command result, not command or encoding
    output = output['result']
    # Interested in interfaces in interfaces dictionary
    output = output['interfaces']

    for interface in sorted(output, key=output.get):
        print 'Interface {}:'.format(interface)
        if 'interfaceCounters' in output[interface]:
            print '   inOctets:  {:,}'.format(output[interface]['interfaceCounters']['inOctets'])
            print '  outOctets:  {:,}'.format(output[interface]['interfaceCounters']['outOctets'])
        else:
            print '  inOctets/outOctets not defined for this interface'

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

