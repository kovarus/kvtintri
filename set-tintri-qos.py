#!/usr/bin/env python
"""

    A basic tool to set the QoS values of a specified virtual machine on the tintri

    If --maxiops is set to 0 then it will remove the upper limit

"""

import argparse
import getpass
import kvtintri

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--storage',
                        required=True,
                        action='store',
                        help='VMStore VMStor IP or hostname')
    parser.add_argument('-u', '--username',
                        required=False,
                        action='store',
                        help='Username to access the VMStore')
    parser.add_argument('-v', '--vm',
                        required=True,
                        action='store',
                        help='VM to set QoS value on')
    parser.add_argument('--miniops',
                        required=False,
                        action='store',
                        help='Minimum normalized IOPs for a virtual machine')
    parser.add_argument('--maxiops',
                        required=True,
                        action='store',
                        help='Max normalized IOPs for a virtual machine')
    args = parser.parse_args()

    return args

def main():

    args = getargs()
    tintri = args.storage
    username = args.username
    vm = args.vm

    if not username:
        username = raw_input("VMStore Username:")

    if not args.miniops:
        args.miniops = 0

    password = getpass.getpass("VMStore Password:")

    session = kvtintri.VMStore.login(tintri, username, password)

    vm_out = session.get_vms()

    virtualmachine = None
    for i in vm_out['items']:
        if i['vmware']['name'] == vm:
            virtualmachine = kvtintri.VirtualMachine.from_uuid(session, i['uuid']['uuid'])
            break
    else:
        print('No virtual machine named %s found.' % vm)

    virtualmachine.qos_max_iops = args.maxiops
    virtualmachine.qos_min_iops = args.miniops
    virtualmachine.update_qos(session)

    # TODO add logic here to verify that it actually changed it

    print('Virtual machine %s updated' % virtualmachine.name)
    print('Min IOPS now: ' +  virtualmachine.qos_min_iops)
    print('Max IOPS now: ' +  virtualmachine.qos_max_iops)

if __name__ == '__main__':
    main()
