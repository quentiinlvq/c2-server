import socket

ip_address = '127.0.0.1'
port_number = 1234

cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cs.connect((ip_address, port_number))

msg = input("Ecris un message :")

while msg != 'quit':
    cs.send(msg.encode())
    msg = cs.recv(1024).decode()
    print(msg)
    msg = input("Enter msg to send :")

cs.close()