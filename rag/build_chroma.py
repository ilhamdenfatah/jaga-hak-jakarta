"""
Membangun ulang database Chroma dari teks bersih di data/dokumen_bersih/.

Kenapa dibangun ulang dan tidak disimpan di repo:
folder Chroma itu file biner, bikin repo membengkak dan rawan bentrok.
Membangunnya ulang hanya butuh beberapa menit di tiap PC dan laptop.

Cara pakai (dari folder utama repo, lingkungan Python sudah aktif):
    python rag/build_chroma.py
"""

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------------------------------------------------------
# Pengaturan (PJ Jalur A boleh menyesuaikan bagian ini)
# ---------------------------------------------------------------
FOLDER_UTAMA = Path(__file__).resolve().parent.parent
FOLDER_DOKUMEN = FOLDER_UTAMA / "data" / "dokumen_bersih"
FOLDER_CHROMA = FOLDER_UTAMA / "rag" / "chroma_db"
NAMA_KOLEKSI = "dokumen_resmi"

# Model embedding yang mendukung banyak bahasa, termasuk Indonesia.
# Model ini diunduh otomatis saat pertama kali dijalankan.
MODEL_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Ukuran potongan teks (jumlah karakter) dan jumlah karakter yang tumpang tindih
UKURAN_POTONGAN = 800
TUMPANG_TINDIH = 100

# Keterangan yang wajib ada di bagian atas setiap file
KETERANGAN_WAJIB = ["JUDUL", "INSTANSI", "TAUTAN", "TANGGAL_AKSES"]


def baca_satu_file(path_file):
    """Membaca satu file teks bersih. Mengembalikan (metadata, isi)."""
    teks = path_file.read_text(encoding="utf-8-sig")
    daftar_baris = teks.splitlines()

    # Baca keterangan di atas sampai ketemu baris pemisah "---"
    keterangan = {}
    nomor_pemisah = None
    for nomor, baris in enumerate(daftar_baris):
        if baris.strip() == "---":
            nomor_pemisah = nomor
            break
        if ":" in baris:
            kunci, nilai = baris.split(":", 1)
            keterangan[kunci.strip().upper()] = nilai.strip()

    if nomor_pemisah is None:
        raise ValueError(
            f"File {path_file.name}: tidak ada baris pemisah '---' "
            "setelah keterangan di bagian atas."
        )

    # Pastikan semua keterangan wajib ada dan tidak kosong
    for kunci in KETERANGAN_WAJIB:
        if keterangan.get(kunci, "") == "":
            raise ValueError(f"File {path_file.name}: keterangan {kunci} belum diisi.")

    isi = "\n".join(daftar_baris[nomor_pemisah + 1:]).strip()
    if isi == "":
        raise ValueError(f"File {path_file.name}: isi dokumen kosong.")

    metadata = {
        "judul": keterangan["JUDUL"],
        "instansi": keterangan["INSTANSI"],
        "tautan": keterangan["TAUTAN"],
        "tanggal_akses": keterangan["TANGGAL_AKSES"],
        "nama_file": path_file.name,
    }
    return metadata, isi


def bangun_chroma(folder_dokumen, folder_chroma, embedding):
    """Membaca semua file .txt, memotongnya, lalu menyimpan ke Chroma."""
    daftar_file = sorted(folder_dokumen.glob("*.txt"))
    if len(daftar_file) == 0:
        raise SystemExit(f"Tidak ada file .txt di {folder_dokumen}")

    pemotong = RecursiveCharacterTextSplitter(
        chunk_size=UKURAN_POTONGAN,
        chunk_overlap=TUMPANG_TINDIH,
    )

    semua_potongan = []
    for path_file in daftar_file:
        metadata, isi = baca_satu_file(path_file)
        dokumen = Document(page_content=isi, metadata=metadata)
        potongan = pemotong.split_documents([dokumen])
        semua_potongan.extend(potongan)
        print(f"{path_file.name}: {len(potongan)} potongan")

    # Hapus database lama supaya tidak ada data dobel
    if folder_chroma.exists():
        shutil.rmtree(folder_chroma)

    Chroma.from_documents(
        documents=semua_potongan,
        embedding=embedding,
        collection_name=NAMA_KOLEKSI,
        persist_directory=str(folder_chroma),
    )
    print(f"Selesai: {len(daftar_file)} dokumen, {len(semua_potongan)} potongan.")
    print(f"Database tersimpan di {folder_chroma}")


if __name__ == "__main__":
    print("Memuat model embedding (pertama kali akan mengunduh, butuh internet)...")
    embedding_lokal = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)
    bangun_chroma(FOLDER_DOKUMEN, FOLDER_CHROMA, embedding_lokal)
