import scapy.all as scapy
import optparse

def getArguments():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--ip', dest= 'ip')
    (options, arguments) = parser.parse_args()
    return options

#Obtiene los dispositivos conectados a una dirección IP dada 
def scan(ip):
    arpRequest = scapy.ARP(pdst= ip)
    broadcast = scapy.Ether(dst= 'ff:ff:ff:ff:ff:ff')
    scapy.arping(ip)
    print('')

    #Pregunta a cada dispositivo conectado a la ip por su respectiva ip y éste le responderá con su ip y dirección mac
    arpRequestBroadcast = broadcast/arpRequest
    answeredList = scapy.srp(arpRequestBroadcast, timeout= 1, verbose = False)[0]

    #Crea un diccionario para almacenar la ip y dirección mac de cada dispositivo que envió una respuesta y las guarda dentro de una lista
    clientsList = []
    for i in answeredList:
        clientDict = {'ip': i[1].psrc, 'mac': i[1].hwsrc}
        clientsList.append(clientDict)
    return clientsList

def printResult(resultsList):
    print('Ip \t\t\tMAC Adress\n-----------------------------------------------')
    for i in resultsList:
        print(i['ip'] + '\t\t' + i['mac'])


options = getArguments()
results = scan(options.ip)
printResult(results)