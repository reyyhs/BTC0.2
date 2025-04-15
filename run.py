import os
import time
import json
from datetime import datetime
from bitcoinlib.keys import Key
import requests
from tqdm import tqdm

# Konfigurasi
MAX_ATTEMPTS = 500  # Kamu bisa ubah jumlah percobaan
LOG_DIR = "logs"
SAVE_FILE = os.path.join(LOG_DIR, "found_wallets.txt")
ATTEMPT_FILE = os.path.join(LOG_DIR, "all_attempts.json")

# Buat folder logs jika belum ada
os.makedirs(LOG_DIR, exist_ok=True)

# Fungsi cek saldo BTC (via BlockCypher)
def check_balance(address):
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['final_balance'] / 1e8  # Satoshi ke BTC
        elif response.status_code == 429:
            print("[!] Terlalu banyak permintaan, istirahat 5 detik...")
            time.sleep(5)
    except Exception as e:
        print(f"[!] Gagal mengambil data: {e}")
    return 0.0

# Simpan wallet dengan saldo > 0
def save_wallet(address, privkey, balance):
    with open(SAVE_FILE, "a") as f:
        f.write("=== WALLET DITEMUKAN ===\n")
        f.write(f"Waktu       : {datetime.now()}\n")
        f.write(f"Address     : {address}\n")
        f.write(f"Private Key : {privkey}\n")
        f.write(f"Balance     : {balance:.8f} BTC\n")
        f.write("=" * 40 + "\n\n")

# Simpan semua percobaan ke file JSON
def log_attempt_json(address, privkey, balance):
    log = {
        "timestamp": str(datetime.now()),
        "address": address,
        "private_key": privkey,
        "balance_btc": balance
    }
    with open(ATTEMPT_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

# Fungsi utama pencarian
def brute_force_wallets(max_attempts=MAX_ATTEMPTS):
    print(f"\n🚀 MULAI SCAN {max_attempts} WALLET BITCOIN...\n")
    for attempt in tqdm(range(1, max_attempts + 1), desc="Scanning"):
        key = Key()
        address = key.address()
        privkey = key.wif()
        balance = check_balance(address)

        # Log setiap percobaan
        log_attempt_json(address, privkey, balance)

        # Tampilkan ke layar
        print(f"[{attempt}] {address} | Balance: {balance:.8f} BTC")

        if balance > 0:
            print("\n🎉 WALLET DENGAN SALDO DITEMUKAN!")
            save_wallet(address, privkey, balance)
            break  # Hentikan jika ditemukan

        time.sleep(1.2)  # Hindari limit API

# Jalankan
if __name__ == "__main__":
    brute_force_wallets()
