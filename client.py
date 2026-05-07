import socket
import time

def fetch_web(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 8888)) # Hubungi Proxy, bukan Web Server!
        request = f"GET /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n"
        s.sendall(request.encode())
        print("Response dari Server:\n", s.recv(4096).decode())

def run_qos_test():
    server_addr = ('127.0.0.1', 9000)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    
    rtts = []
    print("\n--- Memulai QoS Test (UDP Ping) ---")
    for i in range(1, 11):
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

    if rtts:
        print("\n--- Statistik ---")
        print(f"Min RTT: {min(rtts):.2f} ms")
        print(f"Avg RTT: {sum(rtts)/len(rtts):.2f} ms")
        print(f"Max RTT: {max(rtts):.2f} ms")
        print(f"Packet Loss: {(10-len(rtts))/10*100}%")

# Contoh cara pakai:
fetch_web("index.html")
run_qos_test()
