import socket
import time
import csv
import argparse
from datetime import datetime

CLIENT_IP = '10.130.49.184'
PROXY_ADDR = ('10.130.49.136', 8080)
PROXY_UDP_ADDR = ('10.130.49.136', 9090)  # UDP lewat proxy port 9090, bukan langsung ke server

def fetch_web(filename):
    print(f"\n--- Meminta File: /{filename} ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CLIENT_IP, 0))
            s.connect(PROXY_ADDR)
            request = f"GET /{filename} HTTP/1.1\r\nHost: proxy\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode())
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
    packet_results = []  # untuk ekspor CSV: (seq, rtt_or_None, status)
    total_bytes = 0
    start_test_time = time.time()

    print("\n--- Memulai QoS Test (UDP Ping via Proxy) ---")
    for i in range(1, 11):
        timestamp = time.time()
        msg = f"Ping {i} {timestamp}"
        total_bytes += len(msg.encode())

        client_socket.sendto(msg.encode(), PROXY_UDP_ADDR)
        try:
            data, _ = client_socket.recvfrom(1024)
            rtt = (time.time() - timestamp) * 1000
            rtts.append(rtt)
            total_bytes += len(data)
            packet_results.append((i, rtt, 'received'))
            print(f"Ping {i}: RTT = {rtt:.2f} ms")
        except socket.timeout:
            packet_results.append((i, None, 'timeout'))
            print(f"Ping {i}: Request timed out")

    end_test_time = time.time()
    test_duration = end_test_time - start_test_time

    if rtts:
        jitter = 0
        if len(rtts) > 1:
            diffs = [abs(rtts[j] - rtts[j-1]) for j in range(1, len(rtts))]
            jitter = sum(diffs) / len(diffs)

        throughput_bps = (total_bytes * 8) / test_duration
        throughput_kbps = throughput_bps / 1000
        packet_loss = ((10 - len(rtts)) / 10) * 100

        print("\n--- Statistik Jaringan (QoS) ---")
        print(f"Min RTT     : {min(rtts):.2f} ms")
        print(f"Avg RTT     : {sum(rtts)/len(rtts):.2f} ms")
        print(f"Max RTT     : {max(rtts):.2f} ms")
        print(f"Packet Loss : {packet_loss:.1f}%")
        print(f"Jitter      : {jitter:.2f} ms")
        print(f"Throughput  : {throughput_kbps:.2f} kbps")

        # Simpan hasil ke file CSV
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"qos_result_{timestamp_str}.csv"

        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Detail per paket
            writer.writerow(['Seq', 'RTT (ms)', 'Status'])
            for seq, rtt, status in packet_results:
                rtt_val = f"{rtt:.2f}" if rtt is not None else "timeout"
                writer.writerow([seq, rtt_val, status])

            # Ringkasan statistik
            writer.writerow([])
            writer.writerow(['Parameter', 'Nilai'])
            writer.writerow(['Min RTT (ms)', f"{min(rtts):.2f}"])
            writer.writerow(['Avg RTT (ms)', f"{sum(rtts)/len(rtts):.2f}"])
            writer.writerow(['Max RTT (ms)', f"{max(rtts):.2f}"])
            writer.writerow(['Packet Loss (%)', f"{packet_loss:.1f}"])
            writer.writerow(['Jitter (ms)', f"{jitter:.2f}"])
            writer.writerow(['Throughput (kbps)', f"{throughput_kbps:.2f}"])

        print(f"Hasil QoS tersimpan ke: {csv_filename}")

def run_tcp_mode():
    print("=== TAHAP 1: Akses File Normal ===")
    fetch_web("index.html")
    fetch_web("osi.html")

    print("\n=== TAHAP 2: Pengujian 404 Not Found ===")
    fetch_web("file_hantu.html")

    print("\n=== TAHAP 3: Pengujian Cache Proxy (MISS & HIT) ===")
    fetch_web("implementation.html")  # Pasti MISS (pertama kali)
    time.sleep(1)
    fetch_web("implementation.html")  # Pasti HIT (kedua kali)

    print("\n=== TAHAP 4: Pengujian Asset Multimedia ===")
    fetch_web("assets/video.mp4")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client Jaringan Komputer')
    parser.add_argument(
        '--mode',
        choices=['tcp', 'udp'],
        help='Mode operasi: tcp (HTTP request) atau udp (QoS testing). Default: jalankan keduanya.'
    )
    args = parser.parse_args()

    if args.mode == 'tcp':
        print("=== MODE TCP: Pengujian HTTP ===")
        run_tcp_mode()

    elif args.mode == 'udp':
        print("=== MODE UDP: QoS Testing ===")
        run_qos_test()

    else:
        # Tanpa argumen: jalankan semua tahap secara berurutan
        print("=== MODE LENGKAP: TCP + UDP ===")
        run_tcp_mode()
        time.sleep(1)
        run_qos_test()