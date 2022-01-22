import subprocess
import optparse
#import re #para expresiones regulares

#agregar opciones de consola para agregar los argumentos
def getArguments():    
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interface', dest = 'interface')
    parser.add_option('-m', '--mac', dest = 'newMac')
    (options, arguments) = parser.parse_args() #options para --interface y arguments para --newMac
    return options

#Cambiar direcciòn MAC
def changeMac(interface, newMac):    
    #Es mejor ejecutar los procesos dentro de una listas para evitar ser Hackeados
    subprocess.call(['ifconfig', interface, 'down'])                #desactivar la interface antes de modificar
    subprocess.call(['ifconfig', interface, 'hw', 'ether', newMac]) #cambiar direcciòn MAC
    subprocess.call(['ifconfig', interface, 'up'])                  #activar inteface
'''
#Obtiene la direcciòn Mac actual para poder imprimir
def getCurrentMac(interface):
    ifconfigResult = subprocess.check_output(['ifconfig', interface])
    macResult = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfigResult)
    
    if macResult:
        return macResult.group(0)
    else: 
        print("No se pudo leer direcciòn MAC")'''

options = getArguments()
changeMac(options.interface, options.newMac)

ifconfigResult = subprocess.check_output(['ifconfig', options.interface])
print(ifconfigResult)
#currentMac = getCurrentMac(options.interface)

#print('Direcciòn MAC actual: ' + str(currentMac))