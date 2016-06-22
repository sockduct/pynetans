#!/usr/bin/env python
#
def func2(mycaller='function call'):
    print 'Did you expect something profound? --brought to you by {}'.format(mycaller)

if __name__ == '__main__':
    func2('main program execution')
    print 'Successfully executed {}.'.format(__name__)
else:
    func2('main program importation')
    print 'Successfully imported {}.'.format(__name__)

