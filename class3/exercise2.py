#!/usr/bin/env python
####################################################################################################
'''Create two SVG image files based on SNMPv3 data

* 1st image file graphs I/O octets for pynet-rtr1/fa4 every 5 minutes for an hour
* 2nd image file graphs I/O unicast packets for same
'''

# Imports
# Delete unused lines/comments!
# Need sys because using it to call main with arguments
import sys

# Globals
#BASE_FILE = 'file1'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'Month Day, Year'
__version__ = '0.0.1'


#class Myclass1(object):
    '''<description>'''

    #__init__(self, param1):
        '''<description>'''
    #    self.param1 = param1

    #method1(self, param1):
        '''<description>'''
    #    pass

#def func1(param1):
    '''<description>'''
    # Do stuff...

def main(args):
    '''<description>'''
    # Do stuff...

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)


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
