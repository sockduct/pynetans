#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
'''<program description> - triple quotes should end on this line if on liner...
'''

# Imports
# Delete unused lines/comments!
# Need sys because using it to call main with arguments
import sys

# Globals
# Note:  Consider using function/class/method default parameters instead of global constants where
# it makes sense
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

