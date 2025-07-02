import httpx
import os
import socket
import time

# --- KONFIGURASI (GANTI DENGAN DATA ANDA) ---
DDNS_HOSTNAME = "jaringan-bisnis-saya.ddns.net" # Ganti dengan hostname DDNS Anda

TELEGRAM_BOT_TOKEN = "GANTI_DENGAN_TOKEN_BOT_ANDA"
TELEGRAM_CHAT_ID = "GANTI_DENGAN_CHAT_ID_ANDA"

# Kredensial Cloudflare
CF_API_TOKEN = "GANTI_DENGAN_API_TOKEN_ANDA"
CF_ACCOUNT_ID = "GANTI_DENGAN_ACCOUNT_ID_ANDA"
CF_LOCATION_NAME_TO_FIND = "Rumah" # Nama persis dari DNS Location Anda

# Path file
IP_FILE_PATH = os.path.join(os.path.dirname(__file__), 'last_ddns.txt')
# ----------------------------------------------------

def get_public_ip_from_ddns(hostname):
    """Mendapatkan alamat IP dari sebuah hostname."""
    print("INFO: Mencari IP publik via DDNS...")
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror as e:
        print(f"ERROR: Gagal me-resolve DDNS hostname {hostname}: {e}")
        return None

def get_last_ip():
    """Membaca IP terakhir yang tersimpan."""
    if not os.path.exists(IP_FILE_PATH):
        return None
    with open(IP_FILE_PATH, 'r') as f:
        return f.read().strip()

def update_last_ip(new_ip):
    """Menyimpan IP baru ke file."""
    with open(IP_FILE_PATH, 'w') as f:
        f.write(new_ip)

def send_telegram_notification(message):
    """Mengirim notifikasi ke Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        httpx.post(url, json=payload, timeout=10)
        print("INFO: Notifikasi Telegram terkirim.")
    except httpx.RequestError as e:
        print(f"ERROR: Gagal mengirim notifikasi Telegram: {e}")

def get_location_id(client):
    """Mencari ID dari DNS Location berdasarkan namanya."""
    print(f"INFO: Mencari ID untuk lokasi bernama '{CF_LOCATION_NAME_TO_FIND}'...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/gateway/locations"
    try:
        r = client.get(url)
        r.raise_for_status()
        locations = r.json().get("result", [])
        for loc in locations:
            if loc.get("name") == CF_LOCATION_NAME_TO_FIND:
                print(f"SUCCESS: Ditemukan! ID Lokasi: {loc['id']}")
                return loc['id']
        print(f"ERROR: Lokasi dengan nama '{CF_LOCATION_NAME_TO_FIND}' tidak ditemukan.")
        return None
    except (httpx.RequestError, KeyError) as e:
        print(f"ERROR: Gagal mengambil daftar lokasi: {e}")
        return None

def update_cloudflare_location(client, location_id, new_ip):
    """Memperbarui IP di Cloudflare DNS Location dengan payload LENGKAP."""
    print(f"INFO: Memperbarui lokasi {location_id} dengan IP {new_ip}...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/gateway/locations/{location_id}"
    
    # Payload LENGKAP untuk memastikan tidak ada pengaturan yang di-reset
    # Ini adalah bagian yang paling penting
    payload = {
    	"name": CF_LOCATION_NAME_TO_FIND, # Nama lokasi Anda
    	"enabled": True,                  # Memastikan lokasi ini tetap aktif
    	"is_default": False,              # Diasumsikan bukan lokasi default
    	"ecs_support": False,             # Opsi EDNS
    	"networks": [                     # STRUKTUR YANG BENAR UNTUK IP
        	{
            	"network": f"{new_ip}/32"
        	}
    	]
	}
    
    try:
        # Gunakan metode PUT karena kita mengganti data utama (IP)
        r = client.put(url, json=payload)
        r.raise_for_status() # Ini akan memicu error jika status code bukan 2xx
        print("✅ SUCCESS: Cloudflare DNS Location berhasil diperbarui dengan benar.")
        return True
    except httpx.RequestError as e:
        print(f"🔥 ERROR: Gagal memperbarui Cloudflare: {e}")
        # Mencoba mencetak respons error dari Cloudflare jika ada
        try:
            print(f"Response Body: {e.response.json()}")
        except:
            pass
        return False

if __name__ == "__main__":
    print("\n--- Memulai Pengecekan IP & Update Cloudflare (Metode httpx) ---")
    
    current_ip = get_public_ip_from_ddns(DDNS_HOSTNAME)
    if not current_ip:
        exit()

    last_ip = get_last_ip()
    print(f"INFO: IP terakhir: {last_ip}, IP sekarang: {current_ip}")
    
    if current_ip == last_ip:
        print("INFO: IP tidak berubah. Tidak ada tindakan.")
        print("--- Pengecekan Selesai ---")
        exit()

    print("CHANGE DETECTED: IP Publik telah berubah.")
    
    # Siapkan client httpx dengan header otentikasi
    headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
    with httpx.Client(headers=headers, timeout=20.0) as client:
        location_id = get_location_id(client)
        
        if location_id:
            time.sleep(1) # Beri jeda sesaat
            success = update_cloudflare_location(client, location_id, current_ip)
            
            if success:
                notification_message = (
                    f"<b>✅ Pembaruan Jaringan Berhasil</b>\n\n"
                    f"Alamat IP Publik telah berubah dan berhasil diperbarui di Cloudflare.\n\n"
                    f"IP Baru: <code>{current_ip}</code>"
                )
                update_last_ip(current_ip)
            else:
                notification_message = (
                    f"<b>🔥 Peringatan Kritis</b>\n\n"
                    f"Alamat IP Publik telah berubah menjadi <code>{current_ip}</code>, "
                    f"namun <b>GAGAL</b> diperbarui di Cloudflare!\n\n"
                    f"Mohon periksa log di server."
                )
        else:
            notification_message = (
                f"<b>🔥 Peringatan Kritis</b>\n\n"
                f"Gagal menemukan ID Lokasi untuk '{CF_LOCATION_NAME_TO_FIND}'. "
                f"Update IP tidak bisa dilanjutkan."
            )
        
        send_telegram_notification(notification_message)

    print("--- Pengecekan Selesai ---")