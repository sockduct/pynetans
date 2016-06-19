#!/usr/bin/env python
####################################################################################################
#
# Template based on recommendations from Matt Harrison in Beginning Python Programming
#
'''Use Netmiko to connect to each of the devices in the database.
   Execute 'show version' on each device.
   Calculate the amount of time required to do this.
   Note, your results will be more reliable if you use Netmiko's send_command_expect() method.
   There is an issue with the Arista vEOS switches and Netmiko's send_command() method.
   For this version use processes instead of serial execution.
'''

# Imports
# Stdlib
from datetime import datetime
import multiprocessing
import sys

# 3rd Party
import django
from netmiko import ConnectHandler
from net_system.models import NetworkDevice

# Globals
# Note:  Consider using function/class/method default parameters instead of global constants where
# it makes sense
#BASE_FILE = 'file1'

# Metadata
__author__ = 'James R. Small'
__contact__ = 'james<dot>r<dot>small<at>outlook<dot>com'
__date__ = 'June 19, 2016'
__version__ = '0.0.1'


def rcmd(cmd, ndev, q):
    '''Execute cmd on ndev, support concurrency.'''
    conn = ConnectHandler(device_type=ndev.device_type, ip=ndev.ip_address,
                          username=ndev.credentials.username,
                          password=ndev.credentials.password, port=ndev.port)
    result = conn.send_command_expect(cmd)

    dict1 = {}
    mydev = ndev.device_name
    output = '\n{} on {}:\n'.format(cmd, mydev)
    output += '=' * 80 + '\n{}\n'.format(result) + '=' * 80
    dict1[mydev] = output
    q.put(dict1)

def main(args):
    '''Setup database access and base functionality.'''
    django.setup()
    start_time = datetime.now()
    net_devs = NetworkDevice.objects.all()
    q = multiprocessing.Queue()
    workers = []
    result_dict = {}
    cmd = 'show version'

    for ndev in net_devs:
        worker = multiprocessing.Process(target=rcmd, args=(cmd, ndev, q))
        worker.start()
        workers.append(worker)

    for worker in workers:
        print worker
        # Wait for worker to exit in manager
        worker.join()

    while not q.empty():
        dict1 = q.get()
        result_dict[dict1.keys()[0]] = dict1.values()[0]
    for ndev in net_devs:
        print result_dict[ndev.device_name]
    end_time = datetime.now()
    print '\nEllapsed time:  {}\n'.format(end_time - start_time)

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

