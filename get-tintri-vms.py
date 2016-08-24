#!/usr/bin/env python

"""

    A sample script to retrieve a list of all the virtual machines and output a nicely formatted table or CSV

"""

import kvtintri
import getpass
import argparse
from prettytable import PrettyTable
import csv


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
    parser.add_argument('--displayuuid',
                        required=False,
                        action='store_true',
                        help='Display the VMStore UUID of the VM')
    parser.add_argument('--csvout',
                        required=False,
                        action='store',
                        help='Output the report to the specified CSV file')
    parser.add_argument('--match',
                        required=False,
                        action='store',
                        help='Return virtual machines that contain the string specified in --match')
    parser.add_argument('--json',
                        required=False,
                        action='store',
                        help='Output JSON')
    args = parser.parse_args()

    return args

def main():
    # TODO add filter for vCenter server

    args = getargs()
    tintri = args.storage
    username = args.username
    outfile = args.csvout

    if not username:
        username = raw_input("VMStore Username: ")

    # password = getpass.getpass("VMStore Password: ")
    password = "!Passw0rd"
    session = kvtintri.VMStore.login(tintri, username, password)

    if args.match:
        virtualmachines = session.get_vms(name=args.match)
    else:
        virtualmachines = session.get_vms()

    vm_list = []
    for vm in virtualmachines['items']:
        vm_list.append(kvtintri.VirtualMachine.from_dict(vm))

    if args.displayuuid:
        out = PrettyTable(['Name', 'UUID', 'vCenter', 'Power', 'QoS Min', 'QoS Max'])
        out.align['Name'] = 'l'
        out.padding_width = 1
        for i in vm_list:
            out.add_row((i.name, i.uuid, i.vcenter, i.power_state, i.qos_min_iops, i.qos_max_iops))


    else:
        out = PrettyTable(['Name', 'vCenter', 'Power', 'QoS Min', 'QoS Max'])
        out.align['Name'] = 'l'
        out.padding_width = 1
        for i in vm_list:
            out.add_row((i.name, i.vcenter, i.power_state, i.qos_min_iops, i.qos_max_iops))


    print out

    if outfile:
        with open(outfile, "w") as f:
            csv_file = csv.writer(f)
            csv_file.writerow((['Name', 'UUID', 'vCenter', 'Power', 'QoS Min', 'QoS Max']))
            for i in vm_list:
                csv_file.writerow((i.name, i.uuid, i.vcenter, i.power_state, i.qos_min_iops, i.qos_max_iops))


    # TODO output JSON as option
    #
    # if args.json:
    #     with open(args.json, "w") as f:
    #         json_file = json.dumps()



if __name__ == '__main__':
    main()
