#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
'''Use Arista's eAPI/pyeapi to allow adding/removing VLANs
   - Support creating both VLAN ID and Name
   - Adding VLANs:
     - Only add VLAN if it isn't yet defined on switch
     - Supported VLAN ID range is from 100-999
     - Syntax:  <script> --name <name> <ID#>
   - Removing VLANs:
     - Only remove VLAN if it exists on switch
     - Syntax:  <script> --remove <ID#>
'''

# Imports
import argparse
import pyeapi  # This uses ~/.eapi.conf for device and authentication information
import sys

# Globals
MY_SWITCH = 'pynet-sw4'
VLAN_MIN = 100
VLAN_MAX = 999

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'May 21, 2016'
__version__ = '0.0.1'


def main(args):
    '''Acquire necessary input options, connect to Arista switch, add/remove/list VLANs
    per CLI args.'''
    help_str = 'VLAN ID ({}-{})'.format(VLAN_MIN, VLAN_MAX)
    parser = argparse.ArgumentParser(
        description='Add/Remove/List VLANs on Arista switch')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
                        default=False)
    groupx = parser.add_mutually_exclusive_group()
    # Fix later...
    #groupx.add_argument('vlanid', type=int, help='Add {}'.format(help_str))
    groupx.add_argument('-a', '--add', type=int, help='Add {}'.format(help_str))
    groupx.add_argument('-r', '--remove', type=int, help='Remove {}'.format(help_str))
    groupx.add_argument('-l', '--list', action='store_true',
                        help='List current VLANs and their names')
    parser.add_argument('-n', '--name', help='Name of VLAN to add/remove')
    args = parser.parse_args()

    # Connect to Arista switch
    pynet_sw = pyeapi.connect_to(MY_SWITCH)

    if args.list:
        output = pynet_sw.enable('show vlan')
        # Extract desired info
        output = output[0]
        output = output['result']
        output = output['vlans']
        print 'VLAN Name                             Status    Interfaces'
        print '---- -------------------------------- --------- --------------------------------'
        for vlan in output:
            vlan_name = output[vlan]['name']
            vlan_status = output[vlan]['status']
            vlan_ints = []
            for interface in output[vlan]['interfaces']:
                vlan_ints.append(interface)
            if vlan_ints == []:
                vlan_ints_lst = '--None--'
            else:
                vlan_ints_lst = ', '.join(sorted(vlan_ints)).replace('hernet', '')
            print '{:>4} {:32} {:9} {}'.format(vlan, vlan_name, vlan_status, vlan_ints_lst)
    else:
        print 'Not implemented!'

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

