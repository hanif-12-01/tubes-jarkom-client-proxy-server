import socket
import threading
import os

PROXY_PORT = 8888
WEB_SERVER_ADDR = ('127.0.0.1', 8000)
CACHE_DIR = "cache/"

if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)

def handle_client(client_conn):
    request = client_conn.recv(1024).decode()
    if not request: return
    
    filename = request.split()[1].lstrip('/')
    cache_path = os.path.join(CACHE_DIR, filename.replace('/', '_'))

    # Cek Cache (HIT)
    if os.path.exists(cache_path):
        print(f"[CACHE HIT] Melayani {filename} dari lokal")
        with open(cache_path, 'r') as f:
            client_conn.sendall(f.read().encode())
    # Cache MISS (Tanya ke Web Server)
    else:
        print(f"[CACHE MISS] Meminta {filename} ke Web Server")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_sock:
                web_sock.connect(WEB_SERVER_ADDR)
                web_sock.sendall(request.encode())
                response = web_sock.recv(4096)
                
                # Simpan ke cache jika sukses 200 OK
                if b"200 OK" in response:
                    with open(cache_path, 'wb') as f:
                        f.write(response)
                
                client_conn.sendall(response)
        except:
            client_conn.sendall(b"HTTP/1.1 504 Gateway Timeout\n\nWeb Server Mati")
    
    client_conn.close()

proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_sock.bind(('127.0.0.1', PROXY_PORT))
proxy_sock.listen(5)

print(f"Proxy jalan di port {PROXY_PORT}...")
while True:
    c, addr = proxy_sock.accept()
    threading.Thread(target=handle_client, args=(c,)).start()