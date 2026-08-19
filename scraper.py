import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://nucleus.web.id/telkomakses/reporting/rekapclosingsurakarta.php"
JSON_FILE = "data.json"

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    # 1. Ambil data lama jika ada
    existing_data = {}
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                records = json.load(f)
                # Buat dictionary dengan TIKET sebagai Key (Anti-Duplikat)
                existing_data = {item['tiket']: item for item in records if 'tiket' in item}
            except json.JSONDecodeError:
                existing_data = {}

    # 2. Parsing baris tabel baru dari Nucleus
    count_new = 0
    for row in rows:
        cols = [td.text.strip() for td in row.find_all('td')]
        
        # Adjust indeks kolom sesuai tabel HTML Nucleus
        if len(cols) >= 9:
            tiket_id = cols[2] # Kolom TIKET
            
            # Validasi agar bukan header tabel
            if tiket_id and tiket_id.lower() != 'tiket':
                data_row = {
                    "jenis": cols[1],
                    "tiket": tiket_id,
                    "nomor_inet": cols[3],
                    "sektor": cols[4],
                    "teknisi": cols[5],
                    "nik": cols[6],
                    "perbaikan": cols[7],
                    "tgl": cols[8]
                }
                
                # Masukkan/Update data (Nomor TIKET unik mencegah duplikasi)
                if tiket_id not in existing_data:
                    count_new += 1
                existing_data[tiket_id] = data_row

    # 3. Simpan kembali ke file data.json
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(existing_data.values()), f, indent=2, ensure_ascii=False)
        
    print(f"Selesai! Data berhasil diperbarui. Tambahan data baru: {count_new}")

if __name__ == "__main__":
    fetch_data()
