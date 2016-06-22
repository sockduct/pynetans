# Based on class 9 lectures

import sys

def func1():
    print 'Hello world'

def func2(arg1='San Francisco', arg2='Dallas', arg3='Denver', arg4=None):
    # Original behavior - 3 arguments passed, arg4 not set
    if not arg4:
        print arg1, arg2, arg3
    # New behavior, arg4 passed/set
    else:
        print arg1, arg2, arg3, arg4

class MyClass(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def sum(self):
        return self.x + self.y

# I inherit all the methods (and __init__) from MyClass
class NewClass(MyClass):
    def product(self):
        return self.x * self.y

def main(args):
    print 'You called main()!'

# Call main and put all logic there per best practices.
# No triple quotes here because not a function!
if __name__ == '__main__':
    # Recommended by Matt Harrison in Beginning Python Programming
    # sys.exit(main(sys.argv[1:]) or 0)
    # Simplied version recommended by Kirk Byers
    print '__name__ == __main__ ({})'.format(__name__)
    main(sys.argv[1:])
else:
    print '__name__ != __main__ ({})'.format(__name__)
    print "I think I've been imported!"

