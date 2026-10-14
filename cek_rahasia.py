"""
Pemeriksa rahasia: mencari API key, token, atau password yang tidak sengaja
tertulis di file repo.

Jalankan sebelum push (dari folder utama repo):
    python cek_rahasia.py

Kalau ada temuan, perbaiki dulu sebelum push.
Nilai rahasianya sengaja tidak ditampilkan di layar, hanya nama file,
nomor baris, dan jenis temuan.
"""

import os
import re
import sys
from pathlib import Path

FOLDER_UTAMA = Path(__file__).resolve().parent

# Folder yang tidak perlu diperiksa
FOLDER_DILEWATI = {".git", ".venv", "venv", "__pycache__", "chroma_db", "node_modules"}

# Jenis file yang diperiksa
EKSTENSI_DIPERIKSA = {
    ".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml",
    ".csv", ".sql", ".cfg", ".ini", ".example",
}

# Daftar pola rahasia: (nama temuan, pola pencarian)
DAFTAR_POLA = [
    ("Token bot Telegram", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b")),
    ("API key Google atau Gemini", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("API key Groq", re.compile(r"gsk_[A-Za-z0-9]{20,}")),
    ("Token JWT (misalnya key Supabase)",
     re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("Header Bearer berisi token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("Password di connection string", re.compile(r"postgres(?:ql)?://[^:\s/]+:([^@\s]+)@")),
    ("Nilai rahasia di baris pengaturan",
     re.compile(r"""(?i)(api[_-]?key|token|secret|password)["']?\s*[:=]\s*["']?[A-Za-z0-9_\-./+=]{16,}""")),
]


def perlu_diperiksa(path_file):
    """Menentukan apakah file ini ikut diperiksa."""
    if path_file.name == "cek_rahasia.py":
        return False
    # File .env asli memang berisi rahasia dan sudah di-ignore git
    if path_file.name == ".env":
        return False
    # Varian lain seperti .env.example atau .env.local tetap diperiksa
    if path_file.name.startswith(".env"):
        return True
    return path_file.suffix.lower() in EKSTENSI_DIPERIKSA


def periksa_satu_file(path_file):
    """Mengembalikan daftar temuan (nomor baris, jenis temuan) di satu file."""
    daftar_temuan = []
    teks = path_file.read_text(encoding="utf-8", errors="ignore")
    for nomor, baris in enumerate(teks.splitlines(), start=1):
        for nama_pola, pola in DAFTAR_POLA:
            cocok = pola.search(baris)
            if cocok is None:
                continue
            # Tulisan contoh seperti [PASSWORD] di connection string bukan rahasia
            if nama_pola == "Password di connection string" and "PASSWORD" in cocok.group(1):
                continue
            daftar_temuan.append((nomor, nama_pola))
    return daftar_temuan


def main():
    jumlah_temuan = 0
    jumlah_file = 0

    for folder, subfolder, daftar_file in os.walk(FOLDER_UTAMA):
        # Buang folder yang dilewati supaya tidak ikut ditelusuri
        subfolder[:] = [nama for nama in subfolder if nama not in FOLDER_DILEWATI]

        for nama_file in daftar_file:
            path_file = Path(folder) / nama_file
            if not perlu_diperiksa(path_file):
                continue
            jumlah_file += 1
            for nomor, jenis in periksa_satu_file(path_file):
                lokasi = path_file.relative_to(FOLDER_UTAMA)
                print(f"TEMUAN  {lokasi}  baris {nomor}  {jenis}")
                jumlah_temuan += 1

    print(f"{jumlah_file} file diperiksa.")
    if jumlah_temuan == 0:
        print("Aman: tidak ada pola rahasia yang terdeteksi.")
    else:
        print(f"{jumlah_temuan} temuan. Perbaiki dulu sebelum push.")
        sys.exit(1)


if __name__ == "__main__":
    main()
