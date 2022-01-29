import netfilterqueue
import scapy.all as scapy

def processPacket(packet):
    scapyPacket = scapy.IP(packet.get_payload()) #Obtiene toda la información del paquete
    if scapyPacket.haslayer(scapy.DNSRR):
        print(scapyPacket.show())
    packet.accept() #Si en lugar de accept usamos drop, la vìctima no tendrà internet

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, processPacket)
queue.run()
