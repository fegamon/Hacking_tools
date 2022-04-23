import base64
a = b'4444'
b = base64.b64encode(a).decode()
print(b)
print(base64.b64decode(b.encode()).decode())

a = b'192.168.1.14'
b = base64.b64encode(a).decode()
print(b)
print(base64.b64decode(b.encode()).decode())