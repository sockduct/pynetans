#!/usr/bin/env python
####################################################################################################
'''Script that:
 * Uses SNMPv3 to monitor router(s) for configuration changes
 * If a configuration change occurs, provide E-mail notification and specify on which router(s)
   the configuration changed
'''

# Imports
# Delete unused lines/comments!
#import sys
import pickle
import snmp_helper

# Globals
#BASE_FILE = 'file1'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'April 23, 2016'
__version__ = '0.0.1'


#class Myclass1(object):
    #'''<description>'''

    #__init__(self, param1):
    #    '''<description>'''
    #    self.param1 = param1

    #method1(self, param1):
    #    '''<description>'''
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
