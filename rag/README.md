# Folder rag: chatbot tanya jawab

Chatbot untuk tab Tanya jawab di halaman Warga. Jawabannya hanya disusun dari dokumen resmi di `data/dokumen_bersih/` dan selalu menyebut sumbernya.

## Cara kerja singkat

1. `dokumen.py` membaca semua file `.txt` di `data/dokumen_bersih/` lalu memotongnya menjadi potongan kecil (sekitar 900 huruf, mengikuti batas pasal atau bagian).
2. `pencarian.py` mencari potongan yang paling cocok dengan pertanyaan memakai BM25, yaitu pencarian kata seperti indeks di buku. Tidak memakai AI dan tidak perlu mengunduh model. Indeks dibangun otomatis saat pertanyaan pertama masuk, kurang dari satu detik.
3. `chatbot.py` mengirim potongan itu dan pertanyaan ke Groq (model `openai/gpt-oss-120b`), lalu mengembalikan jawaban dan daftar sumber.
4. `jawaban_cadangan.py` berisi jawaban tulisan tangan untuk pertanyaan demo utama. Dipakai hanya kalau Groq tidak bisa dihubungi.

Tidak ada folder database. File `build_chroma.py` dan folder `rag/chroma_db/` tidak dipakai lagi.

## Kesepakatan dengan halaman Warga

```python
from rag.chatbot import jawab

hasil = jawab("Apa syarat KJP Plus?")
# hasil["jawaban"]  teks jawaban
# hasil["sumber"]   daftar {"judul", "tautan", "tanggal_akses"}, kosong kalau informasi tidak tersedia
```

Fungsi `jawab` tidak pernah menghentikan program, termasuk saat internet putus atau Groq bermasalah.

## Isian .env

- `GROQ_API_KEY` wajib.
- `GROQ_MODEL` boleh dikosongkan. Kalau kosong, dipakai `openai/gpt-oss-120b`.
- `GROQ_MODEL_CADANGAN` boleh dikosongkan. Kalau kosong, dipakai `openai/gpt-oss-20b`. Model ini dipakai saat model utama kena batas pemakaian.

Paket gratis Groq membatasi sekitar 8.000 token per menit untuk setiap model, dan satu pertanyaan memakai sekitar 2.000 sampai 2.500 token. Karena itu chatbot memakai dua model bergantian, menunggu sebentar kalau keduanya penuh, dan menyimpan jawaban selama aplikasi berjalan sehingga pertanyaan yang sama tidak memakai kuota lagi.

## Menambah atau mengganti dokumen

Taruh file `.txt` baru di `data/dokumen_bersih/` dengan kepala file seperti dokumen lain (Judul, Instansi, Jenis, Nomor, Tautan, Tanggal, Diakses, Catatan, lalu baris `=====`). Matikan Streamlit lalu jalankan ulang supaya dokumen baru terbaca. Kalau dokumen sumber jawaban cadangan berubah, periksa ulang isi `jawaban_cadangan.py`.

## Uji sebelum dipakai

Jalankan dari folder utama repo:

```
python -m rag.uji_chatbot --cari       uji pencarian saja, tanpa Groq
python -m rag.uji_chatbot --cadangan   uji jawaban cadangan seolah-olah Groq mati
python -m rag.uji_chatbot              uji lengkap dengan Groq asli (sekitar 25 permintaan)
```
