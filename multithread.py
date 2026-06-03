import threading
import subprocess
import time

def jalankan_client(id_client):
    print(f"[START] Client {id_client} mulai mengirim request...")
    # Mengeksekusi file client.py menggunakan terminal secara background
    # Ubah "python" menjadi "python3" atau "py" jika terjadi error
    try:
        subprocess.run(["python", "client.py"], check=True, capture_output=True, text=True)
        print(f"[DONE] Client {id_client} berhasil menerima balasan.")
    except Exception as e:
        print(f"[ERROR] Client {id_client} gagal: {e}")

if __name__ == "__main__":
    print("=== MEMULAI PENGUJIAN MULTI-CLIENT KONKUREN ===")
    
    # Sesuai modul, minimal 5 client konkuren. Kamu bisa ganti angkanya jadi 10, 20, dsb.
    JUMLAH_CLIENT = 5 
    threads = []

    start_waktu = time.time()

    # Membangkitkan banyak client secara bersamaan
    for i in range(JUMLAH_CLIENT):
        t = threading.Thread(target=jalankan_client, args=(i+1,))
        threads.append(t)
        t.start()
        # Jeda 0.5 detik antar pembuatan client agar Proxy tidak "kaget" tiba-tiba
        time.sleep(0.5) 

    # Menunggu semua client selesai bekerja
    for t in threads:
        t.join()

    total_waktu = time.time() - start_waktu
    print(f"\n=== PENGUJIAN SELESAI DALAM {total_waktu:.2f} DETIK ===")