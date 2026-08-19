import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Ambil credential dari environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL dan Key tidak ditemukan di environment variables!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

URL_NUCLEUS = "https://nucleus.web.id/telkomakses/reporting/rekapclosingsurakarta.php"

def fetch_and_push_to_supabase():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(URL_NUCLEUS, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Gagal mengambil data dari Nucleus: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    
    records_to_upsert = []

    for row in rows:
        cols = [td.text.strip() for td in row.find_all('td')]
        
        if len(cols) >= 9:
            tiket_id = cols[2]
            
            # Abaikan baris header
            if tiket_id and tiket_id.lower() != 'tiket':
                # Sesuaikan nama kunci di bawah dengan NAMA KOLOM di tabel Supabase kamu
                record = {
                    "jenis": cols[1],
                    "tiket": tiket_id,
                    "nomor_inet": cols[3],
                    "sektor": cols[4],
                    "teknisi": cols[5],
                    "nik": cols[6],
                    "perbaikan": cols[7],
                    "tanggal": cols[8] # Sesuaikan nama kolom tanggal di Supabase
                }
                records_to_upsert.append(record)

    if records_to_upsert:
        print(f"Mengirim {len(records_to_upsert)} data ke Supabase...")
        # Upsert otomatis memperbarui data jika 'tiket' sudah ada, atau menambah jika baru
        response = supabase.table("dataupload").upsert(records_to_upsert, on_conflict="tiket").execute()
        print("Berhasil memasukkan data ke Supabase!")
    else:
        print("Tidak ada data yang ditemukan untuk diunggah.")

if __name__ == "__main__":
    fetch_and_push_to_supabase()
