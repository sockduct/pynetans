#!/usr/bin/env python

from net_system.models import NetworkDevice
import django

django.setup()

# Variable name can't use a hyphen! ('-')
temp_rtr3 = NetworkDevice(
    device_name='temp-rtr3',
    device_type='cisco_ios',
    ip_address='192.0.2.13',
    port=22,
)
# If you don't save it, it's not retained!!!
temp_rtr3.save()
print 'temp-rtr3:  {}'.format(temp_rtr3)

temp_rtr4 = NetworkDevice.objects.get_or_create(
    device_name='temp-rtr4',
    device_type='cisco_ios',
    ip_address='192.0.2.14',
    port=22,
)
print 'temp-rtr4:  {}'.format(temp_rtr4)

