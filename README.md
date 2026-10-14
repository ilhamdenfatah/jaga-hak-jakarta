# Jaga Hak Jakarta

Prototipe demonstrasi untuk stan PPKD Jakarta Barat di Jakarta Job Fair 2026 (SMESCO Hall, Pancoran, 22 dan 23 Oktober 2026).

Sistem ini membantu warga memahami perubahan desil dan hak bantuan (KJP Plus, KJMU, dan program lain), menyiapkan berkas pengajuan, dan membantu kelurahan mengelola pengajuan secara otomatis lewat n8n.

Ini prototipe. Sistem tidak terhubung dengan sistem resmi mana pun, dan semua datanya fiktif.

## Isi repo

| Folder | Isi | Yang mengedit |
|---|---|---|
| `app/` | Aplikasi Streamlit: halaman Warga dan halaman Kelurahan | Koordinator, PJ Jalur C |
| `rag/` | Script chatbot (LangChain, RAG, Chroma) | PJ Jalur A |
| `data/` | Dokumen bersih, tabel aturan program, data simulasi | PJ Jalur A (`dokumen_bersih`, `aturan_program`), PJ Jalur B (`simulasi`) |
| `n8n/` | Cadangan JSON workflow n8n | PJ Jalur B, Koordinator |
| `docs/` | Panduan dan catatan | Koordinator |

Aturan sederhananya: setiap orang hanya mengedit foldernya sendiri.

## Menyiapkan di komputer

Langkah ini dilakukan sekali di setiap PC atau laptop. Perintah di bawah untuk Windows (PowerShell). Untuk macOS atau Linux, ganti `.venv\Scripts\activate` dengan `source .venv/bin/activate`, dan `copy` dengan `cp`.

1. Ambil repo:

   ```
   git clone <alamat repo>
   cd jaga-hak-jakarta
   ```

2. Buat lingkungan Python dan pasang paket:

   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Buat file pengaturan pribadi:

   ```
   copy .env.example .env
   ```

   Buka `.env`, lalu isi nilainya. API key adalah milik sendiri dan jangan dibagikan ke siapa pun.

4. Bangun database Chroma dari dokumen bersih (butuh internet saat pertama kali, karena model embedding diunduh):

   ```
   python rag/build_chroma.py
   ```

5. Menjalankan aplikasi: perintahnya akan ditambahkan di sini setelah kerangka aplikasi di folder `app/` selesai.

## Cara kerja sehari-hari di repo

Semua orang yang punya akses commit langsung ke cabang `main`, tanpa pull request.

1. Ambil perubahan terbaru dulu: `git pull`
2. Kerjakan file di folder sendiri.
3. Sebelum push, jalankan pemeriksa rahasia: `python cek_rahasia.py`. Kalau ada temuan, perbaiki dulu.
4. Simpan dan kirim:

   ```
   git add .
   git commit -m "pesan singkat tentang perubahan"
   git push
   ```

Anggota tim yang tidak punya akses repo menyerahkan hasil kerja lewat folder Google Drive bersama. PJ jalur atau koordinator yang memasukkannya ke repo.

## Yang tidak boleh masuk repo

- API key, token bot Telegram, password database, dan file `.env`. Pakai `.env` untuk kode Python, dan credential n8n untuk workflow.
- Data pribadi asli (NIK, KK, dan sejenisnya). Semua data adalah data fiktif.
- File PDF sumber asli. Simpan di Google Drive. Yang masuk repo hanya teks bersih di `data/dokumen_bersih/`.
- Folder database Chroma (`rag/chroma_db/`). Folder ini dibangun ulang di tiap perangkat dengan `python rag/build_chroma.py`.

## Aturan main proyek

1. Prototipe demonstrasi. Tidak terhubung dan tidak boleh diklaim terhubung dengan Cek Bansos, SIKS-NG, JAKI, sistem pendaftaran KJP Plus dan KJMU, atau sistem resmi lain.
2. Hanya data fiktif. Dokumen contoh ditandai "CONTOH".
3. Sistem tidak menghitung, memprediksi, atau mengubah desil. Hasil pemeriksaan program berbunyi "dapat diajukan", bukan "pasti berhak". Keputusan ada di instansi berwenang.
4. Kelayakan program ditentukan oleh tabel aturan tertulis, bukan tebakan AI.
5. Jawaban chatbot bersumber dari dokumen resmi dan menyebut sumbernya. Kalau informasinya tidak ada di dokumen, jawabannya "tidak tersedia".
6. Tidak ada komentar politik dan tidak ada penilaian terhadap kinerja instansi atau pejabat tertentu.
