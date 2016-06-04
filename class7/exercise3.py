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
version_added: "?.?.?"
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

# Imports
import pyeapi
from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            vlan=dict(required=True, type='str'),
            name=dict(required=False, type='str'),
        ),
        supports_check_mode=True
    )
    
    
    # Connect to Arista switch
    pynet_sw = pyeapi.connect_to(MY_SWITCH)

    group = Group(module)

    module.debug('Group instantiated - platform %s' % group.platform)
    if group.distribution:
        module.debug('Group instantiated - distribution %s' % group.distribution)

    rc = None
    out = ''
    err = ''
    result = {}
    result['name'] = group.name
    result['state'] = group.state

    if group.state == 'absent':

        if group.group_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = group.group_del()
            if rc != 0:
                module.fail_json(name=group.name, msg=err)

    elif group.state == 'present':

        if not group.group_exists():
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

    if group.group_exists():
        info = group.group_info()
        result['system'] = group.system
        result['gid'] = info[2]

    module.exit_json(**result)


if __name__ == '__main__':
    main()

