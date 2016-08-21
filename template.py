#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
# Progressively updated:  v0.0.7
# Last change:  August 20, 2016
#
# Save below this line
#--------------------------------------------------------------------------------------------------
#
# Template version used:  0.0.6
#
'''<program description> - triple quotes should end on this line if on liner...
'''

# Future Imports - Must be first, provides Python 2/3 interoperability
from __future__ import print_function       # print(<strings...>, file=sys.stdout, end='\n')
from __future__ import division             # 3/2 == 1.5, 3//2 == 1
from __future__ import absolute_import      # prevent implicit relative imports in v2.x
# This one more risky...
from __future__ import unicode_literals     # all string literals treated as unicode strings
# Enforce things required in v3.x:  https://docs.python.org/2/library/__future__.html
# See http://python-future.org/compatible_idioms.html
#
# For future consideration:
#from builtins import *

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
# Only test for Python 3 compatibility:  pylint --py3k <script>.py
# pylint <script>.py
#   Score should be >= 8.0
#
# python warning options:
# * -Qwarnall - Believe check for old division usage
# * -t - issue warnings about inconsitent tab usage
# * -3 - warn about Python 3.x incompatibilities
#
# python3 warning options:
# * -b - issue warnings about mixing strings and bytes
#
# Future:
# * Testing - doctest/unittest/other
# * Logging
#

