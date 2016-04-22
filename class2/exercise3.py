#!/usr/bin/env python
####################################################################################################
'''
Write a script that connects to the lab pynet-rtr1, logins, and executes the
'show ip int brief' command.
'''

import telnetlib
import time
import socket
import sys
import getpass

TELNET_PORT = 23
TELNET_TIMEOUT = 6

class Router(object):
    '''A class to represent a Cisco router'''

    def __init__(self, ip_addr, username, password):
        self.ip_addr = ip_addr
        self.username = username
        self.password = password
        self.connection = telnetlib.Telnet()

    def _login(self):
        '''
        Login to network device
        '''
        output = self.connection.read_until("sername:", TELNET_TIMEOUT)
        self.connection.write(self.username + '\n')
        output += self.connection.read_until("ssword:", TELNET_TIMEOUT)
        self.connection.write(self.password + '\n')
        return output

    def telnet_connect(self):
        '''
        Establish telnet connection
        '''
        try:
            self.connection.open(self.ip_addr, TELNET_PORT, TELNET_TIMEOUT)
        except socket.timeout:
            sys.exit("Connection timed-out")

        # Login
        return self._login()

    def disable_paging(self, paging_cmd='terminal length 0'):
        '''
        Disable the paging of output (i.e. --More--)
        '''
        return self.send_command(paging_cmd)

    def send_command(self, cmd):
        '''
        Send a command down the telnet channel

        Return the response
        '''
        cmd = cmd.rstrip()
        self.connection.write(cmd + '\n')
        time.sleep(1)
        return self.connection.read_very_eager()

def main():
    '''
    Write a script that connects to the lab pynet-rtr1, logins, and executes the
    'show ip int brief' command.
    '''
    ip_addr = raw_input("IP address: ")
    ip_addr = ip_addr.strip()
    username = 'pyclass'
    password = getpass.getpass()

    myrouter = Router(ip_addr, username, password)
    output = myrouter.telnet_connect()

    time.sleep(1)
    myrouter.connection.read_very_eager()
    myrouter.disable_paging()

    output = myrouter.send_command('show ip int brief')

    print "\n\n"
    print output
    print "\n\n"

    myrouter.connection.close()

if __name__ == "__main__":
    main()

