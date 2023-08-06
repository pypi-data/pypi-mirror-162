#!/usr/bin/env python3
import argparse
import glob
import os
import sys
import subprocess
import pathlib


def broadcast(interface):
    """
    Send a ping to the ipv6 multicast address on the interface the device might be at. This triggers IPv6 neighbor
    discovery on the interface so the device shows up in the neighbor address table
    """

    # Shells out to `ping` since the ping binary can send ICMP traffic without root privileges
    subprocess.run(['ping', '-c', '2', '-I', interface, 'ff02::1'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def get_neighbor(interface):
    """
    Get the IPv6 link local neighbors of the USB interface
    """
    res = subprocess.run(['ip', '-6', 'neigh', 'show', 'dev', interface], stdout=subprocess.PIPE)
    raw = res.stdout.decode()
    for line in raw.splitlines():
        if 'FAILED' in line:
            continue
        if 'lladdr' not in line:
            continue
        line = line.strip()
        part = line.split()
        return part[0]
    return None


def find_name(interface):
    """
    Find the USB device information for the USB device that provides the network interface
    """
    path = f'/sys/class/net/{interface}/device'
    if not os.path.islink(path):
        return None

    usb_device = pathlib.Path(path).resolve().parents[0]
    name = ''
    if os.path.isfile(usb_device / 'manufacturer'):
        with open(usb_device / 'manufacturer', 'r') as handle:
            name += handle.read().strip()
    if os.path.isfile(usb_device / 'product'):
        with open(usb_device / 'product', 'r') as handle:
            product = handle.read().strip()
            if product.startswith(f'{name} '):
                name = ''
            name += ' ' + product
    if os.path.isfile(usb_device / 'serial'):
        with open(usb_device / 'serial', 'r') as handle:
            name += ' / ' + handle.read().strip()

    return name.strip()


def find_possible_interfaces():
    interfaces = set()
    for path in glob.glob('/sys/class/net/*/device/interface'):
        with open(path, 'r') as handle:
            raw = handle.read()
        if 'RNDIS' in raw or 'CDC Ethernet' in raw:
            part = path.split('/')
            interfaces.add(part[4])
    return interfaces


def main():
    parser = argparse.ArgumentParser("Find USB tethered phones")
    parser.add_argument('--interface', '-i', help='Interface name', metavar='INTERFACE', action='append')
    parser.add_argument('--addr', '-a', help='Return only the address', action='store_true')
    parser.add_argument('filter', nargs='*')
    args = parser.parse_args()

    forced = False
    if args.interface is None:
        interfaces = find_possible_interfaces()
    else:
        forced = True
        interfaces = args.interface

    table = []
    for i in interfaces:
        address = get_neighbor(i)
        if address is None:
            broadcast(i)
        address = get_neighbor(i)
        if address is None:
            pass

        # Only show the interface specific failure when an interface was manually selected
        if address is None and forced:
            sys.stderr.write(f'{i}: no response\n')

        if address is None:
            continue

        name = find_name(i)
        if name is None or name == '':
            name = 'Unknown device'

        if len(args.filter) > 0:
            match_all = True
            for f in args.filter:
                if f not in name:
                    match_all = False
            if not match_all:
                continue

        table.append([name, address, i])

    if len(table) == 0:
        sys.stderr.write("No devices found\n")
        exit(1)

    name_length = 0
    for row in table:
        if len(row[0]) > name_length:
            name_length = len(row[0])

    for row in table:
        if args.addr:
            print(f'{row[1]}%{row[2]}')
            continue
        print(row[0].rjust(name_length, ' '), '   ', f'{row[1]}%{row[2]}')


if __name__ == '__main__':
    main()
