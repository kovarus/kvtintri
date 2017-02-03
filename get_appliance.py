#!/usr/bin/env python
"""


"""

import argparse
import getpass
import kvtintri
import json
from prettytable import PrettyTable

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
    args = parser.parse_args()

    return args

def main():

    args = getargs()
    tintri = args.storage
    username = args.username


    if not username:
        username = raw_input("VMStore Username:")


    password = getpass.getpass("VMStore Password:")

    session = kvtintri.VMStore.login(tintri, username, password)

    output = session.get_appliance()

    # print json.dumps(output, indent=4)

    out = PrettyTable(['locator', 'status', 'state', 'diskType'])
    out.align['locator'] = 'l'
    out.padding_width = 1
    for i in output[0]['disks']:
        out.add_row((i['locator'], i['status'], i['state'], i['diskType']))

    print out

if __name__ == '__main__':
    main()
