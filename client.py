import socket
import time

CLIENT_IP = '10.130.66.40'
PROXY_ADDR = ('10.130.64.199', 8080)
SERVER_UDP_ADDR = ('10.130.65.241', 9000)

def fetch_web(filename):
    print(f"\n--- Meminta File: /{filename} ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CLIENT_IP, 0)) # Menggunakan IP Client khusus
            s.connect(PROXY_ADDR) 
            request = f"GET /{filename} HTTP/1.1\r\nHost: proxy\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode())
            
            # Ambil potongan kecil untuk mem-print status HTTP-nya saja
            response = s.recv(1024)
            status_line = response.split(b'\r\n')[0].decode(errors='ignore')
            print(f"Status dari Proxy/Server: {status_line}")
            
    except Exception as e:
        print(f"Gagal terhubung ke Proxy: {e}")

def run_qos_test():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((CLIENT_IP, 0))
    client_socket.settimeout(1.0)
    
    rtts = []
    total_bytes = 0
    start_test_time = time.time()
    
    print("\n--- Memulai QoS Test (UDP Ping) ---")
    for i in range(1, 11):
        timestamp = time.time()
        # Format payload sesuai ketentuan modul PDF
        msg = f"Ping {i} {timestamp}"
        total_bytes += len(msg.encode())
        
        client_socket.sendto(msg.encode(), SERVER_UDP_ADDR)
        try:
            data, _ = client_socket.recvfrom(1024)
            rtt = (time.time() - timestamp) * 1000
            rtts.append(rtt)
            total_bytes += len(data)
            print(f"Ping {i}: RTT = {rtt:.2f} ms")
        except socket.timeout:
            print(f"Ping {i}: Request timed out")

    end_test_time = time.time()
    test_duration = end_test_time - start_test_time

    if rtts:
        # Hitung Jitter menggunakan rumus deviasi (selisih absolut antar RTT)
        jitter = 0
        if len(rtts) > 1:
            diffs = [abs(rtts[j] - rtts[j-1]) for j in range(1, len(rtts))]
            jitter = sum(diffs) / len(diffs)
            
        throughput_bps = (total_bytes * 8) / test_duration
        throughput_kbps = throughput_bps / 1000

        print("\n--- Statistik Jaringan (QoS) ---")
        print(f"Min RTT     : {min(rtts):.2f} ms")
        print(f"Avg RTT     : {sum(rtts)/len(rtts):.2f} ms")
        print(f"Max RTT     : {max(rtts):.2f} ms")
        print(f"Packet Loss : {((10-len(rtts))/10)*100:.1f}%")
        print(f"Jitter      : {jitter:.2f} ms")
        print(f"Throughput  : {throughput_kbps:.2f} kbps")

if __name__ == "__main__":
    # Menguji file dari dosen
    print("=== TAHAP 1: Akses File Normal ===")
    fetch_web("index.html")
    fetch_web("osi.html")
    
    print("\n=== TAHAP 2: Pengujian 404 Not Found ===")
    fetch_web("file_hantu.html")
    
    print("\n=== TAHAP 3: Pengujian Cache Proxy (MISS & HIT) ===")
    fetch_web("implementation.html") # Pasti MISS (pertama kali)
    time.sleep(1)
    fetch_web("implementation.html") # Pasti HIT (kedua kali)
    
    print("\n=== TAHAP 4: Pengujian Asset Multimedia ===")
    # Akan MISS pertama kali lalu tersimpan di cache sebagai data binary
    fetch_web("assets/video.mp4")
    
    time.sleep(1)
    run_qos_test()