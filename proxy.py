import socket
import threading
import os
import time
from datetime import datetime

PROXY_IP = '10.130.49.136'
PROXY_PORT = 8080
PROXY_UDP_PORT = 9090
WEB_SERVER_ADDR = ('10.130.49.153', 8000)
WEB_SERVER_UDP_ADDR = ('10.130.49.153', 9000)
CACHE_DIR = "cache/"

if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR)

def handle_client(client_conn, client_addr):
    try:
        request = client_conn.recv(1024).decode()
        if not request: return

        path = request.split()[1]
        filename = path.lstrip('/')
        if filename == "": filename = "index.html"

        cache_path = os.path.join(CACHE_DIR, filename.replace('/', '_'))
        start_time = time.time()

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                content = f.read()
            duration = (time.time() - start_time) * 1000
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [PROXY LOG] IP:{client_addr[0]} | HIT  | {path} | {len(content)} bytes | {duration:.2f} ms")
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
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] [PROXY LOG] IP:{client_addr[0]} | MISS | {path} | {len(response)} bytes | {duration:.2f} ms")
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

def handle_udp_proxy():
    """UDP Proxy pada port 9090: meneruskan paket UDP dari client ke web server port 9000"""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((PROXY_IP, PROXY_UDP_PORT))
    print(f"UDP Proxy berjalan di {PROXY_IP}:{PROXY_UDP_PORT}")

    while True:
        try:
            data, client_addr = udp_sock.recvfrom(1024)

            # Forward ke UDP echo server di web server
            fwd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            fwd_sock.settimeout(1.0)
            fwd_sock.sendto(data, WEB_SERVER_UDP_ADDR)

            try:
                response, _ = fwd_sock.recvfrom(1024)
                udp_sock.sendto(response, client_addr)
            except socket.timeout:
                pass
            finally:
                fwd_sock.close()

        except Exception:
            pass

# Jalankan UDP Proxy di thread background
threading.Thread(target=handle_udp_proxy, daemon=True).start()

proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_sock.bind((PROXY_IP, PROXY_PORT))
proxy_sock.listen(5)

print(f"Proxy Server berjalan di {PROXY_IP}:{PROXY_PORT}...")
while True:
    c, addr = proxy_sock.accept()
    threading.Thread(target=handle_client, args=(c, addr)).start()