import socket

def fetch_web(filename):
    print(f"\n--- Meminta file: /{filename} ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 8080)) # Ke Proxy
            request = f"GET /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n"
            s.sendall(request.encode())
            response = s.recv(4096).decode()
            print(response)
    except Exception as e:
        print(f"Gagal terhubung ke Proxy: {e}")

if __name__ == "__main__":
    # Skenario sesuai screenshot Tahap 3
    fetch_web("index.html")    # Harusnya 200 OK
    fetch_web("missing.html")  # Harusnya 404 Not Found
    fetch_web("page.html")     # Request Pertama -> Proxy Log MISS
    fetch_web("page.html")     # Request Kedua   -> Proxy Log HIT
