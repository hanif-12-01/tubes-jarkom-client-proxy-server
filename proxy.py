import socket
import threading
import os
import time

PROXY_IP = '127.0.0.11'
PROXY_PORT = 8080
WEB_SERVER_ADDR = ('127.0.0.10', 8000)
CACHE_DIR = "cache/"

if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)

def handle_client(client_conn, client_addr):
    try:
        request = client_conn.recv(1024).decode()
        if not request: return
        
        path = request.split()[1]
        filename = path.lstrip('/')
        if filename == "": filename = "index.html"
        
        # Bersihkan nama file agar aman disimpan di Windows
        cache_path = os.path.join(CACHE_DIR, filename.replace('/', '_'))
        start_time = time.time()

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                content = f.read()
            duration = (time.time() - start_time) * 1000
            print(f"[PROXY LOG] IP:{client_addr[0]} | HIT  | {path} | {duration:.2f} ms")
            client_conn.sendall(content)

        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_sock:
                web_sock.settimeout(2.0)
                web_sock.connect(WEB_SERVER_ADDR)
                
                # Memaksa server menutup koneksi setelah selesai mengirim file
                request = request.replace("HTTP/1.1\r\n", "HTTP/1.1\r\nConnection: close\r\n")
                web_sock.sendall(request.encode())
                
                response = b""
                while True:
                    chunk = web_sock.recv(4096)
                    if not chunk: break
                    response += chunk
                
                # Simpan ke cache lokal hanya jika response 200 OK
                if b"200 OK" in response:
                    with open(cache_path, 'wb') as f:
                        f.write(response)
                
                duration = (time.time() - start_time) * 1000
                print(f"[PROXY LOG] IP:{client_addr[0]} | MISS | {path} | {duration:.2f} ms")
                client_conn.sendall(response)
                
    except socket.timeout:
        if os.path.exists("status/504.html"):
            with open("status/504.html", "rb") as f: content = f.read()
            header = f"HTTP/1.1 504 Gateway Timeout\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
            client_conn.sendall(header.encode() + content)
        else:
            client_conn.sendall(b"HTTP/1.1 504 Gateway Timeout\r\n\r\nGateway Timeout")
            
    except Exception as e:
        if os.path.exists("status/502.html"):
            with open("status/502.html", "rb") as f: content = f.read()
            header = f"HTTP/1.1 502 Bad Gateway\r\nContent-Type: text/html\r\nContent-Length: {len(content)}\r\nConnection: close\r\n\r\n"
            client_conn.sendall(header.encode() + content)
        else:
            client_conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\nBad Gateway")
            
    finally:
        client_conn.close()

proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_sock.bind((PROXY_IP, PROXY_PORT))
proxy_sock.listen(5)

print(f"Proxy Server berjalan di {PROXY_IP}:{PROXY_PORT}...")
while True:
    c, addr = proxy_sock.accept()
    threading.Thread(target=handle_client, args=(c, addr)).start()