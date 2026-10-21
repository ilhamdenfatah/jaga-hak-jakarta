"""
Membaca dokumen bersih dan memotongnya menjadi potongan kecil untuk pencarian.

Setiap file .txt di data/dokumen_bersih/ berbentuk:

    Judul: ...
    Instansi: ...
    Jenis: ...
    Nomor: ...
    Tautan: ...
    Tanggal: ...
    Diakses: ...
    Catatan: ...
    ========================================
    (isi dokumen)

Format lama (JUDUL, INSTANSI, TAUTAN, TANGGAL_AKSES, lalu baris ---) juga tetap terbaca.
"""

import os
import re

FOLDER_PROYEK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER_DOKUMEN = os.path.join(FOLDER_PROYEK, "data", "dokumen_bersih")

# Panjang satu potongan, dalam jumlah huruf. Cukup untuk satu pasal pendek atau beberapa butir.
PANJANG_POTONGAN = 900

# Nama kunci di kepala file, diseragamkan. Kiri: tulisan di file (huruf kecil). Kanan: nama yang dipakai di kode.
NAMA_KUNCI = {
    "judul": "judul",
    "instansi": "instansi",
    "jenis": "jenis",
    "nomor": "nomor",
    "tautan": "tautan",
    "tautan rujukan": "tautan",
    "tanggal": "tanggal",
    "diakses": "tanggal_akses",
    "tanggal_akses": "tanggal_akses",
    "catatan": "catatan",
}

# Baris yang menandai awal bagian baru, supaya potongan tidak memotong di tengah pasal atau bab
POLA_AWAL_BAGIAN = re.compile(
    r"^(Pasal \d+|BAB [IVXLC]+|Bagian [A-Z]|[A-Z]\. [A-Z]|[IVX]+\. [A-Z]|LAMPIRAN|[A-Z][A-Z ,()/&?-]{8,}$)"
)


def adalah_garis_pemisah(baris):
    """Baris ===== (format baru) atau --- (format lama)."""
    teks = baris.strip()
    if len(teks) >= 3 and set(teks) == {"="}:
        return True
    if teks == "---":
        return True
    return False


def ambil_tautan_pertama(teks):
    """Mengambil alamat web pertama dari isian Tautan. Contoh: 'https://a.go.id (catatan)' menjadi 'https://a.go.id'."""
    hasil = re.search(r"https?://[^\s;|)]+", teks)
    if hasil:
        return hasil.group(0)
    # Alamat tanpa https, misalnya 'edu.jakarta.go.id/kjp'
    hasil = re.search(r"[a-z0-9.-]+\.go\.id[^\s;|)]*", teks)
    if hasil:
        return "https://" + hasil.group(0)
    return ""


def baca_satu_file(jalur_file):
    """Mengembalikan dict berisi kepala dokumen dan isi. None kalau formatnya tidak dikenali."""
    with open(jalur_file, encoding="utf-8") as berkas:
        semua_baris = berkas.read().splitlines()

    nomor_pemisah = None
    for nomor in range(len(semua_baris)):
        if adalah_garis_pemisah(semua_baris[nomor]):
            nomor_pemisah = nomor
            break
    if nomor_pemisah is None:
        return None

    kepala = {}
    for baris in semua_baris[:nomor_pemisah]:
        if ":" not in baris:
            continue
        kunci, nilai = baris.split(":", 1)
        kunci = kunci.strip().lower()
        if kunci in NAMA_KUNCI:
            kepala[NAMA_KUNCI[kunci]] = nilai.strip()

    isi = "\n".join(semua_baris[nomor_pemisah + 1:]).strip()

    return {
        "nama_file": os.path.basename(jalur_file),
        "judul": kepala.get("judul", os.path.basename(jalur_file)),
        "instansi": kepala.get("instansi", ""),
        "tautan": ambil_tautan_pertama(kepala.get("tautan", "")),
        "tanggal": kepala.get("tanggal", ""),
        "tanggal_akses": kepala.get("tanggal_akses", ""),
        "catatan": kepala.get("catatan", ""),
        "isi": isi,
    }


def potong_isi(isi):
    """Memotong isi dokumen menjadi potongan sekitar PANJANG_POTONGAN huruf, mengikuti batas baris dan bagian."""
    potongan = []
    sekarang = []
    panjang_sekarang = 0

    for baris in isi.splitlines():
        baris = baris.strip()
        if baris == "":
            continue

        awal_bagian_baru = POLA_AWAL_BAGIAN.match(baris) is not None
        sudah_cukup_panjang = panjang_sekarang >= PANJANG_POTONGAN * 0.5

        # Mulai potongan baru kalau ketemu judul bagian baru (dan potongan sekarang sudah lumayan),
        # atau kalau potongan sekarang sudah terlalu panjang.
        if sekarang and ((awal_bagian_baru and sudah_cukup_panjang) or panjang_sekarang + len(baris) > PANJANG_POTONGAN):
            potongan.append("\n".join(sekarang))
            sekarang = []
            panjang_sekarang = 0

        sekarang.append(baris)
        panjang_sekarang = panjang_sekarang + len(baris) + 1

    if sekarang:
        potongan.append("\n".join(sekarang))
    return potongan


def muat_semua_potongan():
    """
    Membaca semua dokumen dan mengembalikan (daftar_dokumen, daftar_potongan).
    Setiap potongan: {"id", "nomor_dokumen", "teks"}.
    """
    daftar_dokumen = []
    daftar_potongan = []

    if not os.path.isdir(FOLDER_DOKUMEN):
        return daftar_dokumen, daftar_potongan

    nama_file_urut = sorted(os.listdir(FOLDER_DOKUMEN))
    for nama_file in nama_file_urut:
        if not nama_file.lower().endswith(".txt"):
            continue
        dokumen = baca_satu_file(os.path.join(FOLDER_DOKUMEN, nama_file))
        if dokumen is None:
            print("Lewati " + nama_file + ": tidak ada garis pemisah ===== atau ---")
            continue

        nomor_dokumen = len(daftar_dokumen)
        daftar_dokumen.append(dokumen)

        for teks in potong_isi(dokumen["isi"]):
            daftar_potongan.append({
                "id": len(daftar_potongan),
                "nomor_dokumen": nomor_dokumen,
                "teks": teks,
            })

    return daftar_dokumen, daftar_potongan
