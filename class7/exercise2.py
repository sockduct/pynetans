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
__version__ = '0.0.2'


def is_int(string1):
    '''Check if passed string is a number.
       This is necessary because isdigit() can't deal with negative numbers.'''
    try:
        int(string1)
        return True
    except ValueError:
        return False

def vlan_get(switch1):
    '''Obtain VLAN database from switch'''
    output = switch1.enable('show vlan')

    # Extract desired info
    output = output[0]
    output = output['result']
    output = output['vlans']

    return output

def vlan_ints(vlan_intdb):
    '''Obtain list of interfaces set to VLAN'''
    my_vlan_ints = []

    for interface in vlan_intdb['interfaces']:
        my_vlan_ints.append(interface)
    if my_vlan_ints == []:
        my_vlan_ints_lst = '--None--'
    else:
        my_vlan_ints_lst = ', '.join(sorted(my_vlan_ints)).replace('hernet', '')

    return my_vlan_ints_lst

def vlan_add(switch1, vlan1, name1, verbose):
    '''Add a VLAN to switch:
       - Support both creating VLAN ID and its Name
       - Only add VLAN if it isn't yet defined on switch
       - Supported VLAN ID range is from VLAN_MIN-VLAN_MAX'''
    output = vlan_get(switch1)

    # First do sanity check - is VLAN in allowed range?
    if int(vlan1) >= VLAN_MIN and int(vlan1) <= VLAN_MAX:
        if verbose:
            print 'VLAN in valid range of {} - {}...'.format(VLAN_MIN, VLAN_MAX)
    else:
        print 'Error:  VLAN must be in range of {} - {} - aborting...'.format(VLAN_MIN, VLAN_MAX)
        return -1

    if verbose:
        print 'Attempting to add VLAN {}...'.format(vlan1)
    if vlan1 not in output:
        if verbose:
            print 'Checking for VLAN...not found on switch'
        cmds = ['vlan {}'.format(vlan1)]
        if name1:
            cmds.append('name {}'.format(name1))
        ### Need to check for errors
        output = switch1.config(cmds)
        if name1:
            if output != [{}, {}]:
                print 'Error occurred while adding VLAN {}, name {}:\n{}'.format(vlan1, name1,
                      output)
                return -1
        elif output != [{}]:
            print 'Error occurred while adding VLAN {}:\n{}'.format(vlan1, output)
            return -1

        if verbose:
            print 'VLAN successfully added'
            if verbose:
                vlan_list(switch1, verbose, vlan1)
        return 1
    else:
        print 'VLAN already exists on switch - aborting...'
        return -1

def vlan_remove(switch1, vlan1, name1, verbose):
    '''Remove a VLAN from switch:
       - Only remove VLAN if it exists on switch'''
    output = vlan_get(switch1)

    # First do sanity check - is VLAN in allowed range?
    if int(vlan1) >= VLAN_MIN and int(vlan1) <= VLAN_MAX:
        if verbose:
            print 'VLAN in valid range of {} - {}...'.format(VLAN_MIN, VLAN_MAX)
    else:
        print 'Error:  VLAN must be in range of {} - {} - not removing...'.format(VLAN_MIN,
              VLAN_MAX)
        return -1

    if verbose:
        print 'Attempting to remove VLAN {}...'.format(vlan1)
    if vlan1 in output:
        if verbose:
            print 'Checking for VLAN...found on switch'
        #
        # If VLAN Name supplied, check that it matches switch configuration
        if name1:
            switch_vlan_name = output[vlan1]['name']
            if name1 == switch_vlan_name:
                if verbose:
                    print 'Checking passed VLAN Name matches switch configuration...Confirmed'
            else:
                print 'Error:  Passed VLAN Name does not match switch VLAN configuration name' + \
                      ' ({}) - Aborting...'.format(switch_vlan_name)
                return -1
        ####
        cmds = ['no vlan {}'.format(vlan1)]
        ### Need to check for errors
        output = switch1.config(cmds)
        if output != [{}]:
            print 'Error occurred while removing VLAN {}:\n{}'.format(vlan1, output)
            return -1
        elif verbose:
            print 'VLAN successfully removed'
            if verbose:
                vlan_list(switch1, verbose)
        return 1
    else:
        print "VLAN doesn't exist on switch - aborting..."
        return -1

def vlan_list(switch1, verbose, vlan1=None, name1=None):
    '''Show VLANs defined on switch
       - Default is to list all VLANs (no vlan or name passed)
       - If a VLAN is passed, just list that VLAN number
       - If a Name is passed, just list that VLAN name'''
    output = vlan_get(switch1)

    print 'VLAN Name                             Status    Interfaces'
    print '---- -------------------------------- --------- --------------------------------'
    if not vlan1 and not name1:
        vlans = output.keys()
        vlans.sort(key=int)
        for vlan in vlans:
            vlan_name = output[vlan]['name']
            vlan_status = output[vlan]['status']
            vlan_ints_lst = vlan_ints(output[vlan])
            print '{:>4} {:32} {:9} {}'.format(vlan, vlan_name, vlan_status, vlan_ints_lst)
    elif vlan1:
        if vlan1 in output:
            vlan_ints_lst = vlan_ints(output[vlan1])
            print '{:>4} {:32} {:9} {}'.format(vlan1, output[vlan1]['name'],
                  output[vlan1]['status'], vlan_ints_lst)
        else:
            print 'Error:  VLAN {} not defined on switch'.format(vlan1)
    elif name1:
        found_vlan_name = False
        # Need to iterate through all VLANs because VLAN name is not guaranteed to be unique
        for vlan in output:
            if name1 == output[vlan]['name']:
                found_vlan_name = True
                vlan_ints_lst = vlan_ints(output[vlan])
                print '{:>4} {:32} {:9} {}'.format(vlan1, output[vlan1]['name'],
                      output[vlan1]['status'], vlan_ints_lst)
        if not found_vlan_name:
            print 'Error:  VLAN Name {} not defined on switch'.format(name1)

def main(args):
    '''Acquire necessary input options, connect to Arista switch, add/remove/list VLANs
    per CLI args.'''
    help_str = 'VLAN ID ({}-{})'.format(VLAN_MIN, VLAN_MAX)
    parser = argparse.ArgumentParser(
        description='Add/Remove/List VLANs on Arista switch')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_true', help='display verbose output',
                        default=False)
    parser.add_argument('vlanid', nargs='?', help='Add (-a implied) {}'.format(help_str),
                        default='-')
    groupx = parser.add_mutually_exclusive_group()
    groupx.add_argument('-a', '--add', help='Add {}'.format(help_str))
    groupx.add_argument('-r', '--remove', help='Remove {}'.format(help_str))
    groupx.add_argument('-l', '--list', action='store_true',
                        help='List current VLANs and their names')
    parser.add_argument('-n', '--name', help='Name of VLAN to add/remove')
    args = parser.parse_args()

    # Debugging:
    ##print 'args:  {}'.format(args)

    if is_int(args.vlanid) and args.add:
        print 'Error:  Use either {} <VLAN_ID> -or- {} -a <VLAN_ID>'.format(sys.argv[0],
              sys.argv[0])
        sys.exit(1)

    # Connect to Arista switch
    pynet_sw = pyeapi.connect_to(MY_SWITCH)

    if args.list:
        vlan_list(pynet_sw, args.verbose)
    elif is_int(args.vlanid):
        vlan_add(pynet_sw, args.vlanid, args.name, args.verbose)
    elif args.add:
        vlan_add(pynet_sw, args.add, args.name, args.verbose)
    elif args.remove:
        vlan_remove(pynet_sw, args.remove, args.name, args.verbose)
    else:
        print 'Usage:  {} {{[-a] <VLAN_ID> | -r <VLAN_ID> '.format(sys.argv[0]) + \
                 '[-n <VLAN_Name>]} | [-l] | [--version]'
        print '            [-v] (Must be paired with a | r | l)'
        sys.exit(1)

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

