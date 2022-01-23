import scapy.all as scapy
from scapy.layers import http


def sniff(interface):
    scapy.sniff(iface= interface, store= False, prn= processSniffedPacket)

def processSniffedPacket(packet):
    if packet.haslayer(http.HTTPRequest) & packet.haslayer(scapy.Raw):
        print(packet.show())

sniff('eth0')