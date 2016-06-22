#!/usr/bin/env python
#
def func1(mycaller='function call'):
    print 'World domination! --brought to you by {}'.format(mycaller)

if __name__ == '__main__':
    func1('main program execution')
    print 'Successfully executed {}.'.format(__name__)
else:
    func1('main program importation')
    print 'Successfully imported {}.'.format(__name__)

