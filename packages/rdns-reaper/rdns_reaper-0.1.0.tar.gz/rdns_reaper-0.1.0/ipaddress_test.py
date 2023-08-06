from ipaddress import IPv4Address, IPv4Network
from netaddr import IPAddress, IPNetwork, IPSet

ip = IPv4Address("1.2.3.4")

addresses = [
    IPv4Address("192.0.2.6"),
    IPv4Address("192.0.3.6"),
    IPv4Address("192.168.1.1"),
    IPv4Address("192.169.1.1"),
]

networks = [IPv4Network("192.0.2.0/28"), IPv4Network("192.168.0.0/16")]

for address in addresses:
    for network in networks:
        if address in network:
            print(f"Found {address}")
            break

print("-" * 10)


addresses = ["192.0.2.6", "192.0.3.6", "192.168.1.1", "192.169.1.1"]
networks = ["192.0.2.0/28", "192.168.0.0/16"]

print(IPSet(addresses).intersection(IPSet(networks)))


print("-" * 10)

addresses = [IPv4Address(x) for x in ["192.0.2.6", "192.0.3.6", "192.168.1.1", "192.169.1.1"]]

networks = [IPv4Network(x) for x in ["192.0.2.0/28", "192.168.0.0/16"]]

for address in addresses:
    for network in networks:
        if address in network:
            print(f"Found {address}")
            break
