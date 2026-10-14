# Folder rag

Script chatbot: membaca dokumen bersih, memotongnya, membuat embedding di komputer lokal, dan menyimpannya di Chroma. Diisi PJ Jalur A.

## Database Chroma tidak disimpan di repo

Folder `rag/chroma_db/` masuk `.gitignore`. Alasannya, isinya file biner yang membuat repo membengkak dan mudah bentrok antar orang. Membangunnya ulang hanya butuh beberapa menit, jadi setiap PC dan laptop membangun sendiri dari teks di `data/dokumen_bersih/`.

Sekali jalan, script ini juga mengunduh model embedding ke perangkat tersebut (butuh internet pertama kali), jadi dua urusan selesai sekaligus.

## Cara membangun ulang

Dari folder utama repo, dengan lingkungan Python aktif:

```
python rag/build_chroma.py
```

Jalankan ulang setiap kali isi `data/dokumen_bersih/` berubah. Folder `rag/chroma_db/` lama dihapus lalu dibuat baru, jadi tidak ada data dobel.

Tiga catatan:

- Tutup aplikasi Streamlit dulu sebelum membangun ulang. Di Windows, folder yang sedang dipakai aplikasi tidak bisa dihapus dan script akan berhenti dengan pesan "Permission denied" atau "Access is denied".
- Jalankan script ini lewat terminal, satu kali per proses. Jangan dipanggil dari dalam aplikasi.
- Kalau ada file di `data/dokumen_bersih/` yang keterangannya kurang, script berhenti dan menyebut nama filenya. Database lama tetap utuh sampai semua file lolos pemeriksaan.

## File

| File | Tugas |
|---|---|
| `build_chroma.py` | Membaca `data/dokumen_bersih/*.txt`, memotong, membuat embedding, menyimpan ke Chroma. Pengaturan (ukuran potongan, nama model) ada di bagian atas file. |

Script tanya jawab (prompt, pemanggilan Groq) menyusul sebagai file terpisah di folder ini.
