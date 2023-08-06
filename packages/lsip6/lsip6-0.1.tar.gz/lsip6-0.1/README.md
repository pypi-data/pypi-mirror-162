# lsip6

Most Linux devices have IPv6 enabled in the kernel. With this tool it's possible to find the link-local IPv6
address of the other end of an point-to-point link.

This tool has been made to find the IPv6 address of a postmarketOS phone connected over USB. It has also been verified
to work with a Mobian PinePhone. The tool is more flexible than that though. If you connect to any device with
an ethernet cable directly without a switch/router in between you've created a point-to-point link that works
with this tool. No need to set up DHCP or remember static IP addresses if IPv6 is running.

## Installation

```shell-session
$ sudo python3 setup.py install
```

## Usage

Without any arguments `lsip6` uses some heuristics to figure out which of the network interfaces are RNDIS USB adapters
and will try to find the IPv6 neighbor of all those adapters and print the results. It will also use the USB hardware
descriptors to come up with a name for the device. This works well with Linux phones since the USB network gadget
that is emulated has the device information set.

```shell-session
$ lsip6
PINE64 PinePhone / postmarketOS     fe80::ac63:afff:fee4:78f5%enp0s20f0u4
  SHIFT SHIFT6mq / postmarketOS     fe80::50c1:98ff:fe88:cb0c%enp0s20f0u3
```

This also works for postmarketOS devices that use the ECM gadget instead of the RNDIS gadget. In this case it's a
Nexus 5. The ECM gadget does not have a nice name set by the postmarketOS initramfs though

```shell-session
$ lsip6
Linux 5.18.1-postmarketos-qcom-msm8974 with ci_hdrc_msm RNDIS/Ethernet Gadget     fe80::f438:9ff:fe56:be29%enp0s20f0u8
```

It is also possible to specify one or more network interfaces to scan instead of letting the heuristics guess which
are the correct ones by specifying the `-i / --interface` argument. With this it's even possible to run it against regular network
links in which case it will just return one random IPv6 address since there might be many devices.

```shell-session
$ lsip6 -i enp0s20f0u3
SHIFT SHIFT6mq / postmarketOS     fe80::50c1:98ff:fe88:cb0c%enp0s20f0u3

$ lsip6 -i wlan0
Unknown device     2a00:xxxx:xxxx:xxxx::100%wlp2s0
```

With the `-a / --addr` argument the tool will only print the IPv6 address which is easier for automation. This is
especially helpful in combination with the `filter...` arguments that are possible. If any filter arguments are
supplied lsip6 will only output results matching _all_ off the filter arguments given. This is case sensitive.

```shell-session
$ lsip6 --addr
fe80::ac63:afff:fee4:78f5%enp0s20f0u4
fe80::50c1:98ff:fe88:cb0c%enp0s20f0u3

$ lsip6 PinePhone
PINE64 PinePhone / postmarketOS     fe80::ac63:afff:fee4:78f5%enp0s20f0u4

$ lsip6 -a PinePhone
fe80::ac63:afff:fee4:78f5%enp0s20f0u4

$ ssh user@`lsip6 -a PinePhone`
```

## How it works

The whole functionality of this tool is build around the IPv6 Neighbour Discovery Protocol (NDP). This is the IPv6
replacement for the functionality provided by ARP on IPv4. When sending traffic to another device on the network your
computer first needs to know the MAC address of that device. If the MAC of the target IP address is unknown the NDP
protocol is used to find this address using a Neighbor Solicitation.

When running the `lsip6` command it will send an ICMPv6 (ping) packet to the network interface to an IPv6 multicast
address. In this case that address is `ff02::1`. This is a multicast address defined by the IPv6 specification that
means "All devices on this link", basically the replacement for a broadcast.

Sending this ping traffic will cause the devices at both ends of the link to start Neighbor Solicitation to figure out
how to talk to eachother. After this the MAC address for the devices will be cached in the kernel, this cache is then
checked by lsip6 to figure out which device exists on the other end.

The equivalent of this tool is roughly this:

```shell-session
$ ping -c 2 -I enp0s20f0u4 ff02::1
result of this ping is ignored, this is just to fill the kernel-side cache

$ ip -6 neigh show dev enp0s20f0u4
fe80::ac63:afff:fee4:78f5 lladdr ae:63:af:e4:78:f5 STALE 

The full address is then {ipaddress}%{interface} to make a usable link-local IPv6 address
```