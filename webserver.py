import socket
import threading
import os
import mimetypes
from datetime import datetime

# Menggunakan IP terpisah untuk simulasi topologi jaringan
SERVER_IP = '127.0.0.10'
HTTP_PORT = 8000
UDP_PORT = 9000

def handle_http_client(connection, address):
    status_code = "200 OK"
    path = "-"
    try:
        request = connection.recv(1024).decode()
        if not request: return
        
        path = request.split()[1]
        filename = path.lstrip('/')
        if filename == "": filename = "index.html"

        # Cek apakah file ada dan BUKAN sebuah folder
        if os.path.exists(filename) and not os.path.isdir(filename):
            # Deteksi tipe file (HTML, CSS, PNG, MP4, dll)
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type: content_type = 'application/octet-stream'

            with open(filename, 'rb') as f:
                content = f.read()
            
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
            response = header.encode() + content
            
        else:
            # Skenario 404: Gunakan file status/404.html dari dosen
            status_code = "404 Not Found"
            if os.path.exists("status/404.html"):
                with open("status/404.html", "rb") as f:
                    content = f.read()
                header = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
                response = header.encode() + content
            else:
                response = b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\nFile Not Found"
            
    except Exception as e:
        # Skenario 500: Gunakan file status/500.html dari dosen
        status_code = "500 Internal Server Error"
        if os.path.exists("status/500.html"):
            with open("status/500.html", "rb") as f:
                content = f.read()
            header = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
            response = header.encode() + content
        else:
            response = f"HTTP/1.1 500 Internal Server Error\r\nConnection: close\r\n\r\nError: {str(e)}".encode()
            
    finally:
        # Mencatat log IP Proxy, Path, Timestamp, dan Status Code
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] LOG: {address[0]} meminta {path} -> {status_code}")
        connection.sendall(response)
        connection.close()

def start_udp_echo():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((SERVER_IP, UDP_PORT))
    print(f"UDP Echo Server berjalan di {SERVER_IP}:{UDP_PORT}")
    while True:
        data, addr = udp_sock.recvfrom(1024)
        udp_sock.sendto(data, addr) # Memantulkan payload yang sama

# Jalankan UDP di thread background
threading.Thread(target=start_udp_echo, daemon=True).start()

# Jalankan HTTP Web Server
http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
http_sock.bind((SERVER_IP, HTTP_PORT))
http_sock.listen(5)

print(f"HTTP Web Server berjalan di {SERVER_IP}:{HTTP_PORT}...")
while True:
    client_conn, client_addr = http_sock.accept()
    threading.Thread(target=handle_http_client, args=(client_conn, client_addr)).start()