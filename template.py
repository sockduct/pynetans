#!/usr/bin/env python
# -*- coding: ascii -*-
# Default is ascii - explicitly coding, could also consider utf-8, latin-1, cp1252, ...
####################################################################################################
#
# Python version(s) used/tested:
# * Python 2.7.11-32 on Windows 7
#----------------------------------------------/cut\------------------------------------------------
#
# Include versions of Python you've tested with, whether it's 32 or 64 bit and which Operating
# System was hosting.
# e.g.:
# * Python 2.7.12-32 on Windows 7
# * Python 2.7.12-32 on Ubuntu 16.04.1
# * Python 3.5.1-64 on CentOS 7.1-1503
# * Python 3.6.0-32 on macOS 10.12
#
#----------------------------------------------\cut/------------------------------------------------
#
# Template version used:  0.1.1
#
#---------------------------------------------------------------------------------------------------
#
# Issues/PLanned Improvements:
# * <first>
# * <second>...
#
#----------------------------------------------/cut\------------------------------------------------
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
# Progressively updated - keep version # below and "template version used" above in sync
# Current version:  0.1.1
# Last change:  January 24, 2017
#
# Remove all text between --/cut\--\cut/-- lines before publishing
#
#----------------------------------------------\cut/------------------------------------------------
'''<module/program description> - triple quotes should end on this line if on liner...
'''

# Future Imports - Must be first, provides Python 2/3 interoperability
from __future__ import print_function       # print(<strings...>, file=sys.stdout, end='\n')
#----------------------------------------------/cut\------------------------------------------------
                                            # Python 2: print 'No newline',  # without __future__
                                            # Python 3: print('No newline', end='')
#----------------------------------------------\cut/------------------------------------------------
from __future__ import division             # 3/2 == 1.5, 3//2 == 1
from __future__ import absolute_import      # prevent implicit relative imports in v2.x
# This one more risky...
from __future__ import unicode_literals     # all string literals treated as unicode strings
#----------------------------------------------/cut\------------------------------------------------
# Enforce things required in v3.x:  https://docs.python.org/2/library/__future__.html
# See http://python-future.org/compatible_idioms.html
#
# For future consideration:
#from builtins import *
#----------------------------------------------\cut/------------------------------------------------

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
__date__ = 'Month Day, Year'    # Date of script creation
__version__ = '0.0.1'           # Script version number starting with 0.0.1


#----------------------------------------------/cut\------------------------------------------------
# Remove any unused constructs - class/def examples
#----------------------------------------------\cut/------------------------------------------------
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
#----------------------------------------------/cut\------------------------------------------------
# No triple quotes here because not a function!
#----------------------------------------------\cut/------------------------------------------------
if __name__ == '__main__':
#----------------------------------------------/cut\------------------------------------------------
    # Recommended by Matt Harrison in Beginning Python Programming
    # sys.exit(main(sys.argv[1:]) or 0)
    # Simplied version recommended by Kirk Byers
#----------------------------------------------\cut/------------------------------------------------
    main(sys.argv[1:])

#----------------------------------------------/cut\------------------------------------------------
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
# * Testing - doctest/unittest/pytest/other
# * Logging
#
#----------------------------------------------\cut/------------------------------------------------

