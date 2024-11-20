import socket
import threading, time

ip_address = '127.0.0.1'
port_number = 1234

THREADS = []
CMD_INPUT = []
CMD_OUTPUT = []

def handle_connection(connection,address):
    msg = connection.recv(1024).decode()
    while msg != 'quit':
        print(msg)
        connection.send(msg.encode())

def close_connection(connection):
    connection.close()

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.bind((ip_address, port_number))
ss.listen(5)

while True:
    connection, address = ss.accept()
    t = threading.Thread(target=handle_connection, args=(connection,address))
    THREADS.append(t)
    t.start()
