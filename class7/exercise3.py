#!/usr/bin/env python
####################################################################################################
# Used https://github.com/ansible/ansible-modules-core/blob/devel/system/group.py as a template
#
# Using Arista's eAPI, write an Ansible module that adds a VLAN (both a VLAN ID and a VLAN name).
# Do this in an idempotent manner i.e. only add the VLAN if it doesn't exist; only change the VLAN
# name if it is not correct.
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

    def __init__(self, module, switch1):
        '''Initialize class instance.'''
        self.module = module
        self.state = module.params['state']
        self.vlan = module.params['vlan']
        self.name = module.params['name']
        #self.conn = None

        '''Establish connection to switch.'''
        self.conn = pyeapi.connect_to(switch1)

    # Enforce valid VLAN values (obtained from StackOverFlow)
    # Ansible throws error for this...
    #@property
    #def vlan(self):
    #    return self._vlan
    #
    #@vlan.setter
    #def vlan(self, v):
    #    if not int(v) >= VLAN_MIN and int(v) <= VLAN_MAX:
    #        raise Exception('VLAN must be an integer in the range {} - {}'.format(VLAN_MIN,
    #                        VLAN_MAX))
    #    self._value = v

    #def openconn(self, switch1):
    #    '''Establish connection to switch.'''
    #    self.conn = pyeapi.connect_to(switch1)

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
        output = self.vlan_get()
    
        if self.vlan in output:
            return True
        else:
            return False
    
    def vlan_name(self):
        '''Return information on VLAN ID and name of VLAN ID on switch (id defined).'''
        if self.vlan_exists():
            output = self.vlan_get()
            return output[self.vlan]['name']
        else:
            return None

    def vlan_name_ok(self):
        '''Check if VLAN's name on switch matches passed name.'''
        switch_vlan_name = self.vlan_name()
        # VLAN name matches
        if self.name == switch_vlan_name and switch_vlan_name is not None:
            return True
        # VLAN name doesn't match or VLAN doesn't exist
        else:
            return False

    def vlan_add(self, change_audit=False):
        '''Add a VLAN to switch:
           - Support both creating VLAN ID and its Name
           - Only add VLAN if it isn't yet defined on switch
           - Supported VLAN ID range is from VLAN_MIN-VLAN_MAX'''
        chg_vlan_name = False
    
        if not self.vlan_exists() or not self.vlan_name_ok():
            if change_audit:
                return (True, 0)
            cmds = ['vlan {}'.format(self.vlan)]
            #if self.name and not self.vlan_name_ok():
            if not self.vlan_name_ok():
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
            if change_audit:
                return (False, 0)
            status = 'VLAN already exists on switch and name is OK - no change...'
            # Use stat_code of None to indicate no change
            return (status, None)
    
    def vlan_remove(self, change_audit=False):
        '''Remove a VLAN from switch:
           - Only remove VLAN if it exists on switch'''
        if self.vlan_exists():
            #
            # If VLAN Name supplied, check that it matches switch configuration
            if self.name and not self.vlan_name_ok():
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
        supports_check_mode = True
    )
    
    

    switch = Switch(module, MY_SWITCH)

    stat_msg = ''
    stat_code = None
    result = {}
    result['name'] = switch.name
    result['state'] = switch.state

    # VLAN should be removed or not exist
    if switch.state == 'absent':

        #print json.dumps({
        #    'debug' : 'Not expecting to go here...'
        #})
        # Needs work...
        if switch.vlan_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (stat_msg, stat_code) = switch.vlan_remove()
            if stat_code != 0:
                module.fail_json(name=switch.vlan, msg=stat_msg)

    # VLAN should be added or exist
    elif switch.state == 'present':

        #print json.dumps({
        #    'debug' : 'Add mode...'
        #})
        if module.check_mode:
            #print json.dumps({
            #    'debug' : 'Check mode...'
            #})
            module.exit_json(changed=switch.vlan_add(change_audit=True))
        # If VLAN not defined, or defined but configured name doesn't match passed name:
        #if not switch.vlan_exists() or (switch.vlan_exists and not switch.vlan_name_ok()):
        if not switch.vlan_exists() or not switch.vlan_name_ok():
            #print json.dumps({
            #    'debug' : 'Change required...'
            #})
            # Do we need this for multiple vlans?
            #(stat_msg, stat_code) = switch.vlan_add(gid=group.gid, system=group.system)
            (stat_msg, stat_code) = switch.vlan_add()
        # VLAN and VLAN Name correct
        else:
            #print json.dumps({
            #    'debug' : 'No change needed...'
            #})
            #(stat_msg, stat_code) = 'No change', 0
            (stat_msg, stat_code) = switch.vlan_add()
            # Should we have separate function just to change switch name?
            #(rc, out, err) = group.group_mod(gid=group.gid)

        # Believe we just need status code check
        #if rc is not None and rc != 0:
        if stat_code != 0 and stat_code is not None:
            #print json.dumps({
            #    'debug' : 'Bad things happened...'
            #})
            module.fail_json(name=switch.vlan, msg=stat_msg)

    if stat_code is None:
        result['changed'] = False
    else:
        result['changed'] = True
    if stat_code == 0:
        result['stdout'] = stat_msg
    else:
        result['stderr'] = stat_msg

    if switch.vlan_exists():
        result['vlan'] = switch.vlan
        result['name'] = switch.vlan_name()

    #result_out = ''
    #for e in result:
    #    result_out += str(e) + ': ' + str(result[e]) + ';  '
    #print json.dumps({
    #    'debug' : 'Results:  {}'.format(result_out)
    #})
    module.exit_json(**result)


if __name__ == '__main__':
    main()

