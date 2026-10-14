"""
Cek koneksi ke database Supabase.

Script ini hanya MEMBACA. Tidak ada data yang diubah.
Isi DATABASE_URL tidak pernah ditampilkan ke layar.
"""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# Langkah 1: cari dan baca file .env di folder utama repo
folder_utama = Path(__file__).resolve().parent.parent
lokasi_env = folder_utama / ".env"

if not lokasi_env.exists():
    print("GAGAL: file .env tidak ditemukan di", folder_utama)
    print("Salin file .env.example menjadi .env, lalu isi DATABASE_URL.")
    sys.exit(1)

load_dotenv(lokasi_env)
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("GAGAL: DATABASE_URL di file .env masih kosong.")
    sys.exit(1)


# Langkah 2: coba menyambung ke database (menunggu paling lama 15 detik)
print("Menyambung ke database...")

try:
    koneksi = psycopg.connect(database_url, connect_timeout=15)
except psycopg.Error as error:
    pesan = str(error)
    print("GAGAL menyambung ke database.")

    if "password authentication failed" in pesan:
        print("Penyebab: password salah. Cek bagian password di DATABASE_URL.")
    elif "Tenant or user not found" in pesan:
        print("Penyebab: nama pengguna salah. Harus berbentuk postgres.<kode_proyek>, bukan sekadar postgres.")
    elif "Network is unreachable" in pesan:
        print("Penyebab: kemungkinan memakai Direct connection. Ganti dengan connection string Session pooler.")
    elif "failed to resolve host" in pesan or "could not translate host name" in pesan or "timeout" in pesan:
        print("Penyebab: alamat server tidak terjangkau. Cek internet dan alamat di DATABASE_URL.")
    else:
        print("Pesan asli dari database:", pesan)

    sys.exit(1)


# Langkah 3: hitung isi tabel aturan_program sebagai bukti koneksi berhasil
with koneksi:
    with koneksi.cursor() as kursor:
        kursor.execute("select count(*) from aturan_program")
        jumlah_baris = kursor.fetchone()[0]

print("BERHASIL. Tabel aturan_program berisi", jumlah_baris, "baris.")
