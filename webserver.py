import socket
import threading
import os

# Konfigurasi
HOST = '127.0.0.1'
HTTP_PORT = 8000
UDP_PORT = 9000

def handle_http_client(connection, address):
    try:
        request = connection.recv(1024).decode()
        if not request: return
        
        # Ambil nama file dari request (misal: GET /index.html)
        filename = request.split()[1].lstrip('/')
        if filename == "": filename = "index.html"

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
            response = f"HTTP/1.1 200 OK\nContent-Length: {len(content)}\n\n{content}"
        else:
            response = "HTTP/1.1 404 Not Found\n\nFile Gak Ada!"
        
        connection.sendall(response.encode())
    except Exception as e:
        print(f"Error HTTP: {e}")
    finally:
        connection.close()

def start_udp_echo():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((HOST, UDP_PORT))
    print(f"UDP Echo Server jalan di port {UDP_PORT}")
    while True:
        data, addr = udp_sock.recvfrom(1024)
        udp_sock.sendto(data, addr) # Pantulkan data balik ke client

# Jalankan HTTP Server dengan Threading
http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
http_sock.bind((HOST, HTTP_PORT))
http_sock.listen(5)

# Jalankan UDP di thread terpisah
threading.Thread(target=start_udp_echo, daemon=True).start()

print(f"Web Server jalan di port {HTTP_PORT}...")
while True:
    client_conn, client_addr = http_sock.accept()
    threading.Thread(target=handle_http_client, args=(client_conn, client_addr)).start()
