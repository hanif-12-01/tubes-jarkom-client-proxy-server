# Tugas Besar Jaringan Komputer  
## Implementasi Client–Proxy–Web Server Berbasis Socket Python

Project ini merupakan tugas besar mata kuliah Jaringan Komputer yang mengimplementasikan arsitektur **Client–Proxy–Web Server** menggunakan Python socket manual.

Sistem ini terdiri dari tiga komponen utama:

1. `client.py`  
2. `proxy.py`  
3. `webserver.py`

Selain itu, project juga menggunakan file HTML, CSS, dan assets pendukung sebagai konten yang dilayani oleh web server.

---

## Anggota Kelompok

| Nama | PIC |
|---|---|
| M. Hanif Al Faiz | client.py |
| Renisa Assyifa Putri | proxy.py |
| Rafi Maheswara | webserver.py |

---

# Dokumentasi Sistem Client–Proxy–Web Server

Dokumentasi ini menjelaskan cara kerja sistem **Client–Proxy–Web Server** pada tugas besar Jaringan Komputer.

Project ini dibuat menggunakan **Python socket manual** tanpa framework web seperti Flask, Django, FastAPI, `requests`, atau `http.server`.

---

## 1. Gambaran Umum Sistem

Sistem ini menggunakan arsitektur:

```text
Client → Proxy → Web Server
```

Artinya, client tidak langsung meminta file ke web server. Semua request HTTP harus melewati proxy terlebih dahulu.

Tujuan dari sistem ini adalah untuk memahami:

- Socket programming
- HTTP request dan HTTP response
- Forwarding request melalui proxy
- Caching pada proxy
- Pengukuran Quality of Service menggunakan UDP
- Multithreading
- Analisis paket menggunakan Wireshark

Secara sederhana:

```text
Client     = peminta layanan
Proxy      = perantara dan cache
Web Server = penyedia file
```

---

## 2. Komponen Utama

Sistem terdiri dari tiga file Python utama:

```text
client.py
proxy.py
webserver.py
```

Selain tiga file Python tersebut, terdapat file pendukung berupa HTML, CSS, status page, dan assets.

Struktur project:

```text
tubes-jarkom-client-proxy-server/
│
├── client.py
├── proxy.py
├── webserver.py
│
├── index.html
├── osi.html
├── tcpip.html
├── qos.html
├── implementation.html
│
├── css/
├── assets/
├── status/
│
└── README.md
```

---

## 3. Fungsi Web Server

`webserver.py` berfungsi sebagai **penyedia file website**.

Web server menyimpan dan melayani file seperti:

```text
index.html
qos.html
osi.html
tcpip.html
implementation.html
css/style.css
assets/
status/
```

Tugas utama web server:

1. Menerima HTTP request dari proxy.
2. Membaca file yang diminta.
3. Mengirim HTTP response ke proxy.
4. Memberikan status `200 OK` jika file ditemukan.
5. Memberikan status `404 Not Found` jika file tidak ditemukan.
6. Menjalankan UDP Echo Server pada port `9000` untuk pengujian QoS.

Contoh response berhasil:

```text
HTTP/1.1 200 OK
```

Contoh response gagal:

```text
HTTP/1.1 404 Not Found
```

Secara sederhana:

```text
Web Server = tempat asli file disimpan
```

---

## 4. Fungsi Proxy

`proxy.py` berfungsi sebagai **perantara antara client dan web server**.

Proxy menerima request dari client, lalu menentukan apakah file yang diminta sudah tersedia di cache atau belum.

Tugas utama proxy:

1. Menerima request dari client.
2. Mengecek apakah file sudah ada di folder cache.
3. Jika file belum ada, proxy meneruskan request ke web server.
4. Jika file sudah ada, proxy langsung mengirim file dari cache.
5. Menyimpan response dari web server ke folder cache.
6. Menampilkan log `CACHE MISS` dan `CACHE HIT`.
7. Mengurangi beban web server.

Secara sederhana:

```text
Proxy = perantara + penyimpan cache
```

---

## 5. Fungsi Client

`client.py` berfungsi sebagai **pihak yang meminta layanan**.

Client memiliki dua fungsi utama:

### A. Mode HTTP

Pada mode HTTP, client mengirim request ke proxy.

Contoh request:

```text
GET /index.html HTTP/1.1
```

Alurnya:

```text
Client → Proxy → Web Server → Proxy → Client
```

Client akan menerima dan menampilkan response dari server melalui proxy.

---

### B. Mode UDP QoS

Pada mode UDP, client mengirim paket UDP ke web server port `9000`.

Tujuannya adalah mengukur performa jaringan.

Parameter yang dihitung:

| Parameter | Penjelasan |
|---|---|
| RTT | Waktu paket pergi dan kembali |
| Packet Loss | Persentase paket yang tidak mendapat balasan |
| Jitter | Variasi delay antar paket |
| Throughput | Laju data yang berhasil diterima |

Secara sederhana:

```text
Client = peminta file + penguji performa jaringan
```

---

## 6. Alur HTTP Secara Detail

Misalnya client meminta file:

```text
/index.html
```

Maka alurnya:

```text
1. Client mengirim request ke Proxy pada port 8080.
2. Proxy menerima request.
3. Proxy mengecek apakah file sudah ada di folder cache.
4. Jika belum ada, proxy meneruskan request ke Web Server port 8000.
5. Web Server mencari file index.html.
6. Web Server mengirim response 200 OK.
7. Proxy menyimpan response ke cache.
8. Proxy mengirim response ke Client.
9. Client menampilkan isi HTML.
```

Alur ini membuktikan bahwa client tidak langsung mengakses web server.

Alur yang benar:

```text
Client → Proxy → Web Server
```

Alur yang tidak boleh digunakan untuk HTTP final:

```text
Client → Web Server
```

---

## 7. Cache MISS

Cache MISS terjadi ketika proxy **belum memiliki file** yang diminta client.

Contoh:

```text
Client meminta /qos.html untuk pertama kali.
```

Karena file belum ada di cache, proxy harus meminta file tersebut ke web server.

Alurnya:

```text
Client → Proxy → Web Server → Proxy → Client
```

Ciri-ciri Cache MISS:

- Proxy meneruskan request ke web server.
- Web server menerima request.
- Proxy menyimpan response ke folder cache.
- Waktu response biasanya lebih lama dibanding Cache HIT.

Contoh log:

```text
CACHE MISS
```

Secara sederhana:

```text
MISS = proxy belum punya file, jadi harus minta ke web server
```

---

## 8. Cache HIT

Cache HIT terjadi ketika proxy **sudah memiliki file** yang diminta client.

Contoh:

```text
Client meminta /qos.html untuk kedua kalinya.
```

Karena file sudah ada di cache, proxy tidak perlu meminta ulang ke web server.

Alurnya:

```text
Client → Proxy → Client
```

Ciri-ciri Cache HIT:

- Proxy langsung mengambil file dari folder cache.
- Web server tidak perlu menerima request baru.
- Waktu response lebih cepat.
- Beban web server berkurang.

Contoh log:

```text
CACHE HIT
```

Secara sederhana:

```text
HIT = proxy sudah punya file, jadi tidak perlu bolak-balik ke web server
```

---

## 9. Perbedaan Cache MISS dan Cache HIT

| Aspek | Cache MISS | Cache HIT |
|---|---|---|
| Kondisi | File belum ada di cache | File sudah ada di cache |
| Arah request | Proxy harus ke web server | Proxy langsung kirim dari cache |
| Response time | Lebih lama | Lebih cepat |
| Beban web server | Bertambah | Berkurang |
| Contoh log | `CACHE MISS` | `CACHE HIT` |

Manfaat utama caching adalah membuat proxy tidak perlu berulang kali meminta file yang sama ke web server.

---

## 10. Folder Cache

Folder `cache` adalah folder yang digunakan proxy untuk menyimpan response yang sudah pernah diminta client.

Contoh isi folder cache:

```text
index.html
qos.html
osi.html
css_style.css
assets_network.png
```

Isi folder cache bergantung pada file apa saja yang pernah diminta melalui proxy.

Folder `cache` aman untuk dihapus karena akan dibuat ulang oleh proxy saat request baru masuk.

Folder `cache` sebaiknya tidak dimasukkan ke GitHub karena merupakan hasil runtime, bukan source code utama.

Disarankan menambahkan ini ke `.gitignore`:

```text
cache/
__pycache__/
*.pyc
```

Menghapus cache berguna saat ingin menguji ulang Cache MISS.

Contoh:

```bash
rmdir /s /q cache
```

---

## 11. Alur UDP QoS

Alur UDP berbeda dengan HTTP.

Untuk HTTP:

```text
Client → Proxy → Web Server
```

Untuk UDP QoS:

```text
Client → Web Server UDP Echo
```

Client mengirim paket UDP ke web server port `9000`.

Web server akan mengirimkan kembali payload yang sama kepada client.

Dari proses ini, client dapat menghitung waktu pengiriman dan penerimaan paket.

Contoh payload UDP:

```text
Ping 1 <timestamp>
Ping 2 <timestamp>
Ping 3 <timestamp>
```

---

## 12. Parameter QoS

QoS atau Quality of Service digunakan untuk mengukur kualitas komunikasi jaringan.

Parameter yang digunakan dalam project ini adalah:

### A. RTT

RTT atau Round Trip Time adalah waktu yang dibutuhkan paket untuk pergi dari client ke server dan kembali lagi ke client.

```text
RTT = waktu diterima - waktu dikirim
```

Semakin kecil RTT, semakin cepat respons jaringan.

---

### B. Packet Loss

Packet loss adalah persentase paket yang tidak mendapat balasan dari server.

```text
Packet Loss = paket hilang / total paket × 100%
```

Packet loss rendah menunjukkan jaringan lebih stabil.

---

### C. Jitter

Jitter adalah variasi delay antar paket.

Jika nilai jitter kecil, maka delay antar paket lebih stabil.

Jika nilai jitter besar, maka jaringan mengalami variasi delay yang tidak konsisten.

---

### D. Throughput

Throughput adalah jumlah data yang berhasil dikirim atau diterima dalam satu satuan waktu.

```text
Throughput = total data berhasil / durasi pengujian
```

Throughput yang lebih besar menunjukkan laju transfer data yang lebih baik.

---

## 13. Pengujian Sistem

Pengujian dilakukan untuk memastikan semua komponen berjalan sesuai fungsi masing-masing.

### A. Pengujian HTTP 200 OK

Tujuan:

```text
Membuktikan bahwa file valid berhasil diminta melalui proxy.
```

Contoh request:

```text
/index.html
/qos.html
/osi.html
/tcpip.html
/implementation.html
```

Output yang diharapkan:

```text
HTTP/1.1 200 OK
```

---

### B. Pengujian 404 Not Found

Tujuan:

```text
Membuktikan bahwa server dapat menangani file yang tidak tersedia.
```

Contoh request:

```text
/missing.html
```

Output yang diharapkan:

```text
HTTP/1.1 404 Not Found
```

---

### C. Pengujian Cache MISS dan HIT

Langkah pengujian:

```text
1. Hapus folder cache.
2. Jalankan webserver.py.
3. Jalankan proxy.py.
4. Request file pertama kali.
5. Proxy menampilkan CACHE MISS.
6. Request file yang sama untuk kedua kalinya.
7. Proxy menampilkan CACHE HIT.
```

---

### D. Pengujian QoS

Langkah pengujian:

```text
1. Jalankan webserver.py.
2. Jalankan client.py.
3. Client mengirim minimal 10 paket UDP.
4. Catat RTT, packet loss, jitter, dan throughput.
```

---

### E. Pengujian Multi-Client

Pengujian multi-client dilakukan dengan menjalankan beberapa instance `client.py` secara bersamaan.

Tujuannya adalah membuktikan bahwa proxy dan web server dapat menangani banyak koneksi sekaligus.

Contoh:

```text
5 terminal menjalankan client.py secara bersamaan
```

Yang diamati:

- Semua client menerima response.
- Proxy tidak crash.
- Web server tidak crash.
- Log request muncul secara bersamaan.
- Cache tetap konsisten.

---

## 14. Cara Menjalankan Lokal

Jalankan tiga program secara berurutan.

### A. Jalankan Web Server

```bash
python webserver.py
```

### B. Jalankan Proxy

```bash
python proxy.py
```

### C. Jalankan Client

```bash
python client.py
```

Urutan menjalankan program:

```text
1. webserver.py
2. proxy.py
3. client.py
```

Alasan urutan ini penting:

```text
client.py membutuhkan proxy.py
proxy.py membutuhkan webserver.py
```

Jika urutannya salah, bisa muncul error seperti:

```text
Connection refused
```

---

## 15. Cara Testing 2 Laptop

Skema testing 2 laptop:

```text
Laptop 1 = Web Server + Proxy
Laptop 2 = Client
```

### Laptop 1

Jalankan web server:

```bash
python webserver.py
```

Lalu buka terminal kedua dan jalankan proxy:

```bash
python proxy.py
```

Laptop 1 menjalankan:

```text
webserver.py → port 8000 dan 9000
proxy.py     → port 8080
```

---

### Laptop 2

Jalankan client:

```bash
python client.py
```

Client diarahkan ke IP Laptop 1 pada port `8080`.

Untuk UDP QoS, client diarahkan ke IP Laptop 1 pada port `9000`.

Contoh:

```text
HTTP request → IP_LAPTOP_1:8080
UDP QoS      → IP_LAPTOP_1:9000
```

Alur HTTP pada testing 2 laptop:

```text
Laptop 2 Client → Laptop 1 Proxy → Laptop 1 Web Server
```

Alur UDP QoS pada testing 2 laptop:

```text
Laptop 2 Client → Laptop 1 Web Server UDP Echo
```

---

## 16. Wireshark

Wireshark digunakan untuk membuktikan alur komunikasi jaringan.

Filter yang digunakan:

```text
tcp.port==8080 || tcp.port==8000 || udp.port==9000
```

Yang diamati:

| Port | Keterangan |
|---|---|
| 8080 | Client ke Proxy |
| 8000 | Proxy ke Web Server |
| 9000 | UDP QoS |
| TCP Conversations | Bukti multi-client |
| HTTP GET | Bukti request HTTP |
| UDP Payload | Bukti paket QoS |

Bukti yang perlu dikumpulkan:

```text
1. HTTP GET ke proxy port 8080.
2. HTTP response dari sistem.
3. UDP packet ke port 9000.
4. Conversations saat multi-client.
```

---

## 17. Kesimpulan

Sistem Client–Proxy–Web Server ini menunjukkan bahwa komunikasi jaringan dapat dibangun menggunakan socket Python manual.

Web server bertugas menyediakan file, proxy bertugas sebagai perantara dan cache, sedangkan client bertugas meminta file dan mengukur performa jaringan.

Mekanisme cache membuat proxy tidak perlu berulang kali meminta file yang sama ke web server.

Request pertama menghasilkan:

```text
CACHE MISS
```

Request berikutnya menghasilkan:

```text
CACHE HIT
```

Dengan adanya pengujian QoS, sistem juga dapat dianalisis dari sisi performa jaringan melalui RTT, packet loss, jitter, dan throughput.

Secara ringkas:

```text
Web Server = penyedia file
Proxy      = perantara dan cache
Client     = peminta file dan penguji QoS
```
