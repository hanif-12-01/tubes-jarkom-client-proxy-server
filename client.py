import socket
import time

def fetch_web(filename):
    print(f"\n--- Meminta file: /{filename} ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Hubungi Proxy (8080), bukan Web Server (8000) langsung!
            s.connect(('127.0.0.1', 8080)) 
            request = f"GET /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n"
            s.sendall(request.encode())
            
            # Menerima respon dari proxy
            response = s.recv(4096).decode()
            print("Response dari Server:\n", response)
    except Exception as e:
        print(f"Gagal terhubung ke Proxy: {e}")

def run_qos_test():
    server_addr = ('127.0.0.1', 9000) # Port UDP di Web Server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0) # Tunggu maksimal 1 detik per paket
    
    rtts = []
    print("\n--- Memulai QoS Test (UDP Ping) ---")
    for i in range(1, 11): # Kirim 10 paket sesuai ketentuan
        start = time.time()
        msg = f"Ping {i}"
        client_socket.sendto(msg.encode(), server_addr)
        try:
            data, addr = client_socket.recvfrom(1024)
            end = time.time()
            rtt = (end - start) * 1000
            rtts.append(rtt)
            print(f"Ping {i}: RTT = {rtt:.2f} ms")
        except socket.timeout:
            print(f"Ping {i}: Request timed out")

    # Statistik QoS (Tugas Hanif)
    if rtts:
        print("\n--- Statistik QoS ---")
        print(f"Min RTT     : {min(rtts):.2f} ms")
        print(f"Avg RTT     : {sum(rtts)/len(rtts):.2f} ms")
        print(f"Max RTT     : {max(rtts):.2f} ms")
        print(f"Packet Loss : {(10-len(rtts))/10*100}%")
        # Jitter sederhana (selisih antar paket) bisa ditambahkan jika perlu
    else:
        print("\n--- Statistik QoS ---")
        print("Packet Loss: 100% (Server tidak merespon)")

if __name__ == "__main__":
    # --- PENGUJIAN TAHAP 3 (HTTP) ---
    # 1. Tes file yang ada (200 OK)
    fetch_web("index.html")
    
    # 2. Tes file yang TIDAK ada (404 Not Found)
    fetch_web("missing.html")
    
    # 3. Tes Caching (MISS lalu HIT)
    fetch_web("page.html") # Yang pertama ini akan MISS di Proxy
    time.sleep(1)          # Jeda sebentar agar log enak dibaca
    fetch_web("page.html") # Yang kedua ini WAJIB HIT di Proxy
    
    # --- PENGUJIAN QoS (UDP) ---
    time.sleep(1)
    run_qos_test()
