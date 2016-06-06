#!/usr/bin/python
####################################################################################################
# Used https://github.com/ansible/ansible-modules-core/blob/devel/system/group.py as a template
#
# Using Arista's eAPI, write an Ansible module that adds a VLAN (both a VLAN ID and a VLAN name).
# Do this in an idempotent manner i.e. only add the VLAN if it doesn't exist; only change the VLAN
# name if it is not correct.
#
# To simplify this process, use the .eapi.conf file to store the connection arguments (username,
# password, host, port, transport).
# 

DOCUMENTATION = '''
---
module: exercise3
author: "James Small"
version_added: "0.0.1"
short_description: Add VLAN to Arista switch
requirements: [ pyeapi ]
description:
    - Add VLAN to Arista switch
options:
    vlan:
        required: true
        description:
            - VLAN ID (1-4094)
    name:
        required: false
        description:
            - Name of the VLAN
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the group should be present or not on the remote host.
'''

EXAMPLES = '''
# Example group command from Ansible Playbooks
- exercise3: vlan=101 name=MyVLAN state=present
'''

# Globals
MY_SWITCH = 'pynet-sw4'
VLAN_MIN = 1
VLAN_MAX = 4094

# Imports
import pyeapi
from ansible.module_utils.basic import *

def is_int(string1):
    '''Check if passed string is a number.
       This is necessary because isdigit() can't deal with negative numbers.'''
    try:
        int(string1)
        return True
    except ValueError:
        return False
    
class Switch(object):
    '''Represent an Arista vswitch to allow adding/removing VLANs'''

    def __init__(self, module):
        '''Initialize class instance.'''
        self.module = module
        self.state = module.params['state']
        self.vlan = module.params['vlan']
        self.name = module.params['name']
        self.conn = None

    # Enforce valid VLAN values (obtained from StackOverFlow)
    @property
    def vlan(self):
        return self._vlan
    #
    @vlan.setter
    def vlan(self, v):
        if not int(v) >= VLAN_MIN and int(v) <= VLAN_MAX:
            raise Exception('VLAN must be an integer in the range {} - {}'.format(VLAN_MIN,
                            VLAN_MAX))
        self._value = v

    def openconn(self, switch1):
        '''Establish connection to switch.'''
        self.conn = pyeapi.connect_to(switch1)

    def vlan_get(self):
        '''Obtain VLAN database from switch'''
        output = self.conn.enable('show vlan')
    
        # Extract desired info
        output = output[0]
        output = output['result']
        output = output['vlans']
    
        return output
    
    def vlan_exists(self):
        '''Check if a VLAN exists on switch.'''
        output = vlan_get(self.conn)
    
        if self.vlan in output:
            return True
        else:
            return False
    
    def vlan_name_ok(self):
        '''Check if VLAN's name on switch matches passed name.'''
        output = vlan_get(self.conn)

        switch_vlan_name = output[self.vlan]['name']
        # VLAN name matches
        if self.name == switch_vlan_name:
            return True
        # VLAN name doesn't match
        else:
            return False

    def named_vlan_exists(self, check1):
        '''Check if a VLAN exists on switch.'''
        output = vlan_get(self.conn)
    
        if self.vlan_exists():
            switch_vlan_name = output[self.vlan]['name']
            # VLAN exists, correct name
            if self.name == switch_vlan_name:
                return True
            # VLAN exists, incorrect name
            else:
                return False
        # VLAN does not exist
        else:
            return False
    
    def vlan_add(self, check1):
        '''Add a VLAN to switch:
           - Support both creating VLAN ID and its Name
           - Only add VLAN if it isn't yet defined on switch
           - Supported VLAN ID range is from VLAN_MIN-VLAN_MAX'''
        chg_vlan_name = False
    
        if not self.vlan_exists():
            cmds = ['vlan {}'.format(self.vlan)]
            if self.name and not self.vlan_name_ok():
                cmds.append('name {}'.format(self.name))
                chg_vlan_name = True
            ### Need to check for errors
            output = self.conn.config(cmds)
            if chg_vlan_name:
                if output != [{}, {}]:
                    status = 'Error occurred while adding VLAN {}, name {}:\n{}'.format(self.vlan,
                             self.name, output)
                    return (status, -1)
            elif output != [{}]:
                status = 'Error occurred while adding VLAN {}:\n{}'.format(self.vlan, output)
                return (status, -1)
    
            return ('Successful', 0)
        else:
            status = 'VLAN already exists on switch - aborting...'
            return (status, 0)
    
    def vlan_remove(self, check1):
        '''Remove a VLAN from switch:
           - Only remove VLAN if it exists on switch'''
        output = vlan_get(switch1)
    
        if self.vlan in output:
            #
            # If VLAN Name supplied, check that it matches switch configuration
            if self.name:
                switch_vlan_name = output[self.vlan]['name']
                if not self.name == switch_vlan_name:
                    status = 'Error:  Passed VLAN Name does not match switch VLAN configuration name' + \
                             ' ({}) - Aborting...'.format(switch_vlan_name)
                    return (status, -1)
            ####
            cmds = ['no vlan {}'.format(self.vlan)]
            ### Need to check for errors
            output = self.conn.config(cmds)
            if output != [{}]:
                status = 'Error occurred while removing VLAN {}:\n{}'.format(self.vlan, output)
                return (status, -1)
            return ('Successful', 0)
        else:
            status = "VLAN doesn't exist on switch - aborting..."
            return (status, 0)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            vlan=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
        ),
        supports_check_mode=True
    )
    
    

    switch = Switch(module)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = switch.name
    result['state'] = switch.state

    # Want VLAN Removed
    if switch.state == 'absent':

        if switch.vlan_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = switch.vlan_remove()
            if rc != 0:
                module.fail_json(name=group.name, msg=err)

    # Want VLAN Added
    elif switch.state == 'present':

        if not switch.vlan_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = group.group_add(gid=group.gid, system=group.system)
        else:
            (rc, out, err) = group.group_mod(gid=group.gid)

        if rc is not None and rc != 0:
            module.fail_json(name=group.name, msg=err)

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True
    if out:
        result['stdout'] = out
    if err:
        result['stderr'] = err

    if switch.vlan_exists():
        info = group.group_info()
        result['system'] = group.system
        result['gid'] = info[2]

    module.exit_json(**result)


if __name__ == '__main__':
    main()

