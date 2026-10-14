# Folder data

| Subfolder | Isi | Yang mengisi |
|---|---|---|
| `dokumen_bersih/` | Teks bersih dari dokumen resmi, siap dimasukkan ke chatbot | PJ Jalur A |
| `aturan_program/` | Tabel aturan program (syarat, tanggal buka dan tutup, sumber) | PJ Jalur A |
| `simulasi/` | Dokumen persona dan data simulasi (300 rumah tangga, 50 pengajuan fiktif) | PJ Jalur B |

PDF sumber asli tidak masuk repo. Simpan di Google Drive bersama.

## Format file di `dokumen_bersih/`

Setiap file berupa teks biasa (`.txt`, disimpan sebagai UTF-8) dengan keterangan di bagian paling atas, lalu satu baris berisi tiga tanda hubung, lalu isi dokumen. Script chatbot membaca keterangan ini supaya setiap jawaban bisa menyebut sumbernya.

```
JUDUL: (judul dokumen asli)
INSTANSI: (nama instansi penerbit)
TAUTAN: (alamat resmi dokumen)
TANGGAL_AKSES: 2026-10-14
---
(isi teks bersih mulai dari sini)
```

Aturan:

- Keempat keterangan (JUDUL, INSTANSI, TAUTAN, TANGGAL_AKSES) wajib ada. Kalau ada yang kosong, pembuatan database chatbot akan berhenti dan menyebut nama filenya.
- Tulis tanggal dengan format tahun-bulan-tanggal.
- Nama file huruf kecil, tanpa spasi, pakai garis bawah. Contoh: `pergub_kjp_plus.txt`.
- Hanya dokumen dari sumber resmi.
- Buang kop surat, nomor halaman, dan daftar isi dari bagian isi.

## Data simulasi

Semua data fiktif. Tanpa NIK, KK, atau data pribadi asli. Dokumen contoh ditandai "CONTOH".
