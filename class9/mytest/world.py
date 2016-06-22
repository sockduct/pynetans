#!/usr/bin/env python
#
class MyClass(object):
    def __init__(self, arg1, arg2, arg3):
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def hello(self):
        print 'Hello {}, {} and {}!'.format(self.arg1, self.arg2, self.arg3)

    def not_hello(self):
        print 'Goodbye {}, {} and {}!'.format(self.arg1, self.arg2, self.arg3)

class MyChildClass(MyClass):
    def __init__(self, arg1, arg2, arg3):
        super(MyChildClass, self).__init__(arg1, arg2, arg3)
        self.language = 'Polish'

    def hello(self):
        print 'Mowisz po polsku?  Dzien dobry {}, {} i {}!'.format(self.arg1, self.arg2, self.arg3)

def func1(mycaller='function call'):
    print 'World domination! --brought to you by {}'.format(mycaller)

if __name__ == '__main__':
    func1('main program execution')
    print 'Successfully executed {}.'.format(__name__)
else:
    func1('main program importation')
    print 'Successfully imported {}.'.format(__name__)

