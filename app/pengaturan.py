"""
Pengaturan bersama untuk halaman Warga dan halaman Kelurahan.

Isinya dua hal:
1. Membaca isi file .env di folder utama repo (alamat database, alamat webhook n8n,
   nama bot Telegram). Isi rahasianya tidak pernah ditampilkan ke layar.
2. Daftar tetap yang dipakai di banyak tempat, misalnya empat status pengajuan.
   Isinya harus sama persis dengan docs/kontrak_data.md.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Folder utama repo adalah satu tingkat di atas folder app/
FOLDER_UTAMA = Path(__file__).resolve().parent.parent
LOKASI_ENV = FOLDER_UTAMA / ".env"

# Baca file .env sekali saat file ini pertama kali dipakai.
# Kalau file .env tidak ada, tidak error di sini. Pengecekannya di fungsi ambil_pengaturan.
load_dotenv(LOKASI_ENV)


def ambil_pengaturan(nama):
    """Mengambil satu isian dari .env. Kalau kosong atau tidak ada, hasilnya teks kosong."""
    nilai = os.getenv(nama)
    if nilai is None:
        return ""
    return nilai.strip()


def file_env_ada():
    """Benar kalau file .env ada di folder utama repo."""
    return LOKASI_ENV.exists()


# Nama isian di .env (sama dengan .env.example)
DATABASE_URL = "DATABASE_URL"
N8N_WEBHOOK_W1_URL = "N8N_WEBHOOK_W1_URL"
N8N_WEBHOOK_W2_URL = "N8N_WEBHOOK_W2_URL"
TELEGRAM_BOT_USERNAME = "TELEGRAM_BOT_USERNAME"
SUMBER_DATA = "SUMBER_DATA"


def ambil_sumber_data():
    """
    Penanda asal pengajuan dari halaman Warga: "uji" selama build, "stan" di hari H.
    Diatur lewat SUMBER_DATA di .env. Kalau kosong atau salah tulis, dianggap "uji",
    supaya data percobaan tidak tercampur dengan pengajuan pengunjung.
    """
    nilai = ambil_pengaturan(SUMBER_DATA).lower()
    if nilai == "stan":
        return "stan"
    return "uji"


# Empat status pengajuan. Urutan ini juga urutan tampil di halaman Kelurahan.
# Sengaja tidak ada "Ditolak" atau "Disetujui": keputusan ada di dinas terkait.
DAFTAR_STATUS = [
    "Diterima",
    "Sedang diverifikasi",
    "Perlu berkas tambahan",
    "Diteruskan ke dinas",
]

# Berapa lama menunggu jawaban database atau n8n sebelum menyerah (detik)
BATAS_TUNGGU_DETIK = 15

# Teks penjelas yang tampil di kedua halaman
TEKS_SIMULASI = (
    "Simulasi untuk demonstrasi di stan PPKD Jakarta Barat. Semua data fiktif. "
    "Sistem ini tidak terhubung ke kelurahan, dinas, atau sistem resmi pemerintah mana pun."
)
