#!/usr/bin/env python
#

# Imports
import sys

try:
    from mytest import func1, func2, func3, MyClass
except ImportError:
    print 'Could not locate mytest - is PYTHONPATH set correctly?'
    sys.exit(-1)

def main():
    print 'Testing mytest functions and main class...'
    func1()
    func2()
    func3()
    myobj = MyClass(1, 2, 3)
    myobj.hello()
    myobj.not_hello()

if __name__ == '__main__':
    main()

