"""
Mengirim data ke n8n lewat webhook.

- Halaman Warga memakai kirim_pengajuan() ke W1 (tombol "Ajukan").
- Halaman Kelurahan memakai kirim_perubahan_status() ke W2 (tombol simpan status).

Bentuk data dan balasan mengikuti docs/kontrak_data.md bagian 9.

Semua fungsi di sini selalu mengembalikan dict, tidak pernah melempar error ke halaman.
Isinya minimal:
    ok                 : benar kalau n8n menyatakan data tersimpan
    pesan              : kalimat untuk ditampilkan (boleh kosong kalau berhasil)
    masalah_teknis     : benar kalau n8n tidak bisa dihubungi atau balasannya tidak dikenali
    mungkin_tersimpan  : benar kalau belum jelas tersimpan atau tidak (misalnya n8n lambat)
Kunci lain dari balasan n8n (misalnya kode_pengajuan, notifikasi_terkirim) ikut diteruskan.
"""

import requests

from pengaturan import (
    BATAS_TUNGGU_DETIK,
    N8N_WEBHOOK_W1_URL,
    N8N_WEBHOOK_W2_URL,
    ambil_pengaturan,
)


def hasil_gagal(pesan, mungkin_tersimpan=False):
    """Bentuk balasan standar saat ada masalah teknis."""
    return {
        "ok": False,
        "pesan": pesan,
        "masalah_teknis": True,
        "mungkin_tersimpan": mungkin_tersimpan,
    }


def kirim_ke_webhook(nama_isian_url, data):
    """
    Mengirim data (dict) sebagai JSON ke alamat webhook yang tertulis di .env.
    nama_isian_url adalah nama isian di .env, misalnya N8N_WEBHOOK_W2_URL.
    """
    alamat = ambil_pengaturan(nama_isian_url)
    if alamat == "":
        return hasil_gagal(nama_isian_url + " di file .env masih kosong. Hubungi koordinator.")

    # Langkah 1: kirim, lalu tangani kalau n8n tidak bisa dihubungi
    try:
        jawaban = requests.post(alamat, json=data, timeout=BATAS_TUNGGU_DETIK)
    except requests.exceptions.Timeout:
        return hasil_gagal(
            "n8n tidak menjawab dalam " + str(BATAS_TUNGGU_DETIK) + " detik. "
            "Data mungkin sudah tersimpan. Muat ulang halaman untuk mengecek sebelum mencoba lagi.",
            mungkin_tersimpan=True,
        )
    except requests.exceptions.ConnectionError:
        return hasil_gagal("Tidak bisa menghubungi n8n. Cek koneksi internet, lalu coba lagi.")
    except requests.exceptions.RequestException:
        return hasil_gagal("Pengiriman ke n8n gagal. Silakan coba lagi.")

    # Langkah 2: periksa kode HTTP
    if jawaban.status_code == 404:
        return hasil_gagal(
            "Alamat webhook tidak dikenali n8n (404). Kemungkinan workflow belum di-publish "
            "atau alamat di .env salah."
        )
    if jawaban.status_code >= 500:
        return hasil_gagal("n8n atau database sedang bermasalah. Data belum tersimpan, silakan coba lagi.")
    if jawaban.status_code != 200:
        return hasil_gagal("n8n membalas dengan kode " + str(jawaban.status_code) + ". Silakan coba lagi.")

    # Langkah 3: baca isi balasan
    try:
        isi = jawaban.json()
    except ValueError:
        return hasil_gagal("Balasan n8n tidak bisa dibaca.", mungkin_tersimpan=True)

    # Kadang n8n membalas dalam bentuk daftar berisi satu item. Ambil item pertamanya.
    if isinstance(isi, list) and len(isi) == 1:
        isi = isi[0]

    if not isinstance(isi, dict) or "ok" not in isi:
        return hasil_gagal("Balasan n8n tidak sesuai format yang disepakati.", mungkin_tersimpan=True)

    # Langkah 4: balasan sesuai kontrak data
    hasil = dict(isi)
    hasil["ok"] = isi.get("ok") is True
    hasil["pesan"] = str(isi.get("pesan") or "")
    hasil["masalah_teknis"] = False
    hasil["mungkin_tersimpan"] = False
    return hasil


def kirim_perubahan_status(kode_pengajuan, status_baru, catatan_petugas, nama_petugas):
    """Halaman Kelurahan ke W2. Catatan dan nama petugas kosong dikirim sebagai null."""
    if catatan_petugas is not None and catatan_petugas.strip() == "":
        catatan_petugas = None
    if nama_petugas is not None and nama_petugas.strip() == "":
        nama_petugas = None

    data = {
        "kode_pengajuan": kode_pengajuan,
        "status_baru": status_baru,
        "catatan_petugas": catatan_petugas,
        "nama_petugas": nama_petugas,
    }
    return kirim_ke_webhook(N8N_WEBHOOK_W2_URL, data)


def kirim_pengajuan(data_pengajuan):
    """
    Halaman Warga ke W1. data_pengajuan berisi kunci persis seperti kontrak data bagian 9.
    Dipakai di tahap halaman Warga.
    """
    return kirim_ke_webhook(N8N_WEBHOOK_W1_URL, data_pengajuan)
