import socket #komunikasi jaringan udp dan tcp
import time #menghitung waktu respons dan QoS


PROXY_HOST = "localhost"
PROXY_PORT = 8080 #sesuai dengan ketentuan tubes makanya portnya 8080
HTTP_TIMEOUT_SECONDS = 5 
RESPONSE_PREVIEW_LIMIT = 1000

UDP_SERVER_HOST = "localhost"
UDP_SERVER_PORT = 9000
UDP_PACKET_COUNT = 10
UDP_TIMEOUT_SECONDS = 1


def build_http_get_request(path):
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {PROXY_HOST}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )


def split_http_response(response_text):
    if "\r\n\r\n" in response_text:
        header_text, body = response_text.split("\r\n\r\n", 1)
    elif "\n\n" in response_text:
        header_text, body = response_text.split("\n\n", 1)
    else:
        header_text, body = response_text, ""

    header_lines = header_text.splitlines()
    status_line = header_lines[0] if header_lines else "(status line tidak ditemukan)"
    return status_line, body


def run_http_mode():
    print("\n=== Mode HTTP/TCP ===")
    path = input("Masukkan path, contoh /index.html: ").strip()

    if not path:
        path = "/"
    elif not path.startswith("/"):
        path = "/" + path

    request = build_http_get_request(path)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(HTTP_TIMEOUT_SECONDS)

            start_time = time.perf_counter()
            client_socket.connect((PROXY_HOST, PROXY_PORT))
            client_socket.sendall(request.encode("utf-8"))

            response_parts = []
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                response_parts.append(data)
            end_time = time.perf_counter()

        response_time_ms = (end_time - start_time) * 1000
        response_text = b"".join(response_parts).decode("utf-8", errors="replace")
        status_line, body = split_http_response(response_text)

        print("\n=== Response dari Proxy ===")
        print(f"Status line  : {status_line}")
        print(f"Response time: {response_time_ms:.2f} ms")
        print("\n=== Isi Response ===")
        print(body[:RESPONSE_PREVIEW_LIMIT] if body else "(body kosong)")

        if len(body) > RESPONSE_PREVIEW_LIMIT:
            print("\n... isi response dipotong agar terminal tetap ringkas ...")
    except ConnectionRefusedError:
        print("Proxy belum aktif atau connection refused.")
        print(f"Pastikan proxy berjalan di {PROXY_HOST}:{PROXY_PORT}.")
    except socket.timeout:
        print("Timeout saat menghubungi proxy.")
        print(f"Pastikan proxy berjalan dan merespons dalam {HTTP_TIMEOUT_SECONDS} detik.")
    except OSError as error:
        print(f"Terjadi error koneksi ke proxy: {error}")


def run_udp_mode():
    print("\n=== Mode UDP/QoS ===")
    print(f"Mengirim {UDP_PACKET_COUNT} paket ke {UDP_SERVER_HOST}:{UDP_SERVER_PORT}")
    print(f"Timeout per paket: {UDP_TIMEOUT_SECONDS} detik\n")

    sent_packets = 0
    received_packets = 0
    successful_payload_bytes = 0
    rtt_values = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.settimeout(UDP_TIMEOUT_SECONDS)
        test_start_time = time.perf_counter()

        for sequence_number in range(1, UDP_PACKET_COUNT + 1):
            timestamp = time.time()
            payload = f"Ping {sequence_number} {timestamp}"
            payload_bytes = payload.encode("utf-8")
            start_time = time.perf_counter()

            try:
                client_socket.sendto(
                    payload_bytes,
                    (UDP_SERVER_HOST, UDP_SERVER_PORT),
                )
                sent_packets += 1

                data, server_address = client_socket.recvfrom(1024)
                end_time = time.perf_counter()

                rtt_ms = (end_time - start_time) * 1000
                rtt_values.append(rtt_ms)
                received_packets += 1
                successful_payload_bytes += len(payload_bytes)

                response = data.decode("utf-8", errors="replace")
                print(
                    f"Paket {sequence_number}: RTT={rtt_ms:.2f} ms "
                    f"dari {server_address[0]}:{server_address[1]} | {response}"
                )
            except socket.timeout:
                print(f"Paket {sequence_number}: Request timed out")
            except OSError:
                print(f"Paket {sequence_number}: Request timed out")

        test_end_time = time.perf_counter()

    lost_packets = sent_packets - received_packets
    packet_loss = (lost_packets / sent_packets) * 100 if sent_packets else 0
    test_duration_seconds = test_end_time - test_start_time
    throughput_bps = (
        (successful_payload_bytes * 8) / test_duration_seconds
        if test_duration_seconds > 0
        else 0
    )

    print("\n=== Ringkasan QoS UDP ===")
    print(f"Packets Sent    : {sent_packets}")
    print(f"Packets Received: {received_packets}")
    print(f"Packet Loss     : {packet_loss:.2f}%")

    if rtt_values:
        min_rtt = min(rtt_values)
        avg_rtt = sum(rtt_values) / len(rtt_values)
        max_rtt = max(rtt_values)
        jitter_values = [
            abs(rtt_values[index] - rtt_values[index - 1])
            for index in range(1, len(rtt_values))
        ]
        jitter = sum(jitter_values) / len(jitter_values) if jitter_values else 0

        print(f"Min RTT         : {min_rtt:.2f} ms")
        print(f"Avg RTT         : {avg_rtt:.2f} ms")
        print(f"Max RTT         : {max_rtt:.2f} ms")
        print(f"Jitter          : {jitter:.2f} ms")
    else:
        print("Min RTT         : -")
        print("Avg RTT         : -")
        print("Max RTT         : -")
        print("Jitter          : -")

    print(f"Throughput      : {throughput_bps:.2f} bps")


def show_menu():
    print("\n=== Client Hanif ===")
    print("1. Mode HTTP/TCP")
    print("2. Mode UDP/QoS")
    print("0. Keluar")


def main():
    while True:
        show_menu()
        choice = input("Pilih mode: ").strip()

        if choice == "1":
            run_http_mode()
        elif choice == "2":
            run_udp_mode()
        elif choice == "0":
            print("Client selesai.")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")


if __name__ == "__main__":
    main()
