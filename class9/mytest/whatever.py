#!/usr/bin/env python
#
def func3(mycaller='function call'):
    print 'Why are you calling me? --brought to you by {}'.format(mycaller)

if __name__ == '__main__':
    func3('main program execution')
    print 'Successfully executed {}.'.format(__name__)
else:
    func3('main program importation')
    print 'Successfully imported {}.'.format(__name__)

