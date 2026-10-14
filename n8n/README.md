# Folder n8n

Workflow n8n hidup di n8n Cloud. Folder ini berisi cadangan JSON-nya, dengan dua fungsi:

1. Cadangan hari H: kalau akun n8n bermasalah, workflow bisa di-import ulang dari file di sini.
2. Riwayat perubahan.

Yang mengedit folder ini: PJ Jalur B dan koordinator.

## Nama file

| Workflow | Nama file |
|---|---|
| W1 Penerimaan pengajuan | `w1-intake.json` |
| W2 Perubahan status | `w2-status.json` |
| W3 Pengingat dan eskalasi | `w3-reminder.json` |
| W4 Laporan harian | `w4-report.json` |
| W5 Kanal komunitas (bonus) | `w5-community.json` |

Satu workflow satu file. Kalau ada versi baru, timpa file lama (riwayat lama tetap bisa dilihat di GitHub). Nama untuk workflow tambahan (misalnya penghubung Telegram) ditentukan bersama koordinator.

## Cara mengambil file JSON dari n8n

1. Buka workflow di n8n Cloud.
2. Di bagian atas kanvas, klik menu Workflow (ikon tiga titik).
3. Pilih Download. File JSON tersimpan di komputer.
4. Ganti nama file sesuai tabel di atas, lalu taruh di folder ini.

Kebalikannya (import ulang): menu Workflow, pilih Import from File, lalu pilih file JSON-nya.

## Aturan sebelum push

1. Push hanya versi workflow yang sudah lolos tes.
2. File JSON dari n8n hanya memuat nama dan ID credential, bukan isi rahasianya. Tetapi kalau ada token atau key yang ditulis langsung di dalam node (misalnya di header HTTP Request), nilainya ikut terbawa ke file.
3. Sebelum push, jalankan dari folder utama repo:

   ```
   python cek_rahasia.py
   ```

   Selain itu, buka file JSON dan cari kata `token`, `key`, dan `Bearer` secara manual.
4. Kalau ada nilai rahasia tertulis langsung di node, pindahkan ke credential n8n dulu, lalu ambil ulang file JSON-nya.
5. Jangan bagikan file JSON ini kepada anggota Jalur B sebelum mereka selesai membangun workflow sendiri, kecuali koordinator memutuskan lain.
