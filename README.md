# Skrip DDNS & Notifikasi untuk Cloudflare Gateway

Proyek ini berisi sebuah skrip Python yang dirancang untuk berjalan di server Linux (khususnya lingkungan *headless* seperti Armbian di STB) untuk memberikan dua fungsionalitas utama:

1.  **Sinkronisasi IP Dinamis (DDNS):** Secara otomatis memperbarui alamat IP Sumber (*Source IPv4 Address*) pada sebuah DNS Location di Cloudflare Zero Trust Gateway.
2.  **Notifikasi Real-time:** Mengirimkan peringatan instan ke Bot Telegram setiap kali terjadi perubahan IP publik.

Skrip ini adalah solusi untuk menjaga agar kebijakan penyaringan konten berbasis DNS dari Cloudflare tetap efektif, bahkan pada koneksi internet dengan alamat IP publik yang dinamis.

## Fitur Utama

  * **Deteksi IP Cerdas:** Menggunakan *hostname* dari layanan DDNS (seperti No-IP) sebagai sumber kebenaran (*single source of truth*) untuk alamat IP publik, menghindari masalah deteksi IP saat berada di belakang WARP atau CG-NAT.
  * **Integrasi Penuh dengan Cloudflare API:** Menggunakan *library* `httpx` untuk berinteraksi langsung dengan API Cloudflare, secara spesifik memperbarui `DNS Location` dengan metode `PUT` yang aman.
  * **Notifikasi Instan via Telegram:** Memberikan peringatan langsung kepada administrator saat IP berubah atau saat terjadi kegagalan dalam proses update, memungkinkan respons yang cepat.
  * **Efisien dan Ringan:** Didesain untuk berjalan di perangkat berdaya rendah seperti STB (Single-Board Computer) dan diotomatisasi menggunakan `systemd` timers untuk keandalan maksimal.
  * **Manajemen Status:** Menyimpan catatan IP terakhir dalam sebuah file lokal untuk mencegah panggilan API yang tidak perlu jika tidak ada perubahan.

## Tumpukan Teknologi (Tech Stack)

  * **Bahasa:** Python 3
  * **Library Utama:** `httpx` (untuk panggilan API), `socket` (untuk resolusi DNS)
  * **Platform Target:** Debian-based Linux (diuji pada Armbian)
  * **Otomatisasi:** `systemd` (services & timers)
  * **Layanan Eksternal:**
      * Cloudflare Zero Trust API
      * Telegram Bot API
      * Layanan DDNS (misalnya, No-IP)

## Cara Penggunaan

1.  **Prasyarat:** Pastikan Anda memiliki Python 3 dan `pip` terinstal.
2.  **Kloning Repositori:**
    ```bash
    git clone https://github.com/faqihudin703/Cloudflare-DDNS-Updater-and-Notifier.git
    cd Cloudflare-DDNS-Updater-and-Notifier
    ```
3.  **Konfigurasi:**
    Buka file skrip utama dan isi semua variabel yang diperlukan di bagian `--- KONFIGURASI (GANTI DENGAN DATA ANDA) ---`, termasuk:
      * `DDNS_HOSTNAME`
      * `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`
      * `CF_ACCOUNT_ID` & `CF_API_TOKEN`
      * `CF_LOCATION_NAME_TO_FIND`

-----

### **Penting: Gunakan *Virtual Environment* (venv)**

Sangat disarankan untuk menginstal dependensi dan menjalankan skrip ini di dalam sebuah **lingkungan virtual Python (venv)** untuk menghindari konflik dengan paket Python milik sistem.

1.  **Buat venv** di dalam folder proyek:
    ```bash
    python3 -m venv venv
    ```
2.  **Aktifkan venv:**
    ```bash
    source venv/bin/activate
    ```
3.  **Instalasi Dependensi** di dalam venv:
    ```bash
    pip install httpx
    ```
4.  Saat skrip dijalankan (baik manual maupun oleh `systemd`), pastikan Anda menggunakan *interpreter* Python dari dalam folder `venv` untuk memastikan semua *library* termuat dengan benar.

-----

## Menjalankan Skrip

Skrip ini dirancang untuk dijalankan secara otomatis. Untuk pengujian manual, aktifkan `venv` terlebih dahulu, lalu jalankan:

```bash
python3 DDNS_Updater_Cloudflare.py
```

Untuk penggunaan produksi, disarankan untuk menjalankannya sebagai layanan `systemd` yang dipicu oleh sebuah *timer*. Pastikan baris `ExecStart` di file `.service` Anda menunjuk ke Python yang ada di dalam `venv` (contoh: `/path/ke/proyek/venv/bin/python3`).

## Kontribusi

Masukan dan kontribusi selalu diterima. Silakan buka *issue* untuk melaporkan *bug* atau mengajukan permintaan fitur baru.
