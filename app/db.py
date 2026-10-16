"""
Membaca data dari database Supabase.

Aturan penting: file ini hanya MEMBACA. Halaman Warga dan halaman Kelurahan tidak
pernah menulis langsung ke database. Menulis selalu lewat n8n (lihat webhook.py),
supaya menyimpan data dan mengabari warga terjadi bersamaan.

Setiap fungsi membuka sambungan baru lalu menutupnya lagi. Sedikit lebih lambat,
tetapi lebih tahan banting kalau internet stan sempat putus.
"""

import pandas as pd
import psycopg
from psycopg.rows import dict_row

from pengaturan import (
    BATAS_TUNGGU_DETIK,
    DATABASE_URL,
    ambil_pengaturan,
    file_env_ada,
)


class DatabaseGagal(Exception):
    """Kesalahan database yang pesannya sudah dalam bahasa awam."""


def terjemahkan_error(pesan_asli):
    """Mengubah pesan error database menjadi kalimat yang bisa dipahami petugas stan."""
    if "password authentication failed" in pesan_asli:
        return "Password database salah. Cek DATABASE_URL di file .env."
    elif "Tenant or user not found" in pesan_asli:
        return "Nama pengguna database salah. Harus berbentuk postgres.<kode_proyek>."
    elif "failed to resolve host" in pesan_asli or "could not translate host name" in pesan_asli:
        return "Alamat database tidak ditemukan. Cek koneksi internet dan alamat di DATABASE_URL."
    elif "timeout" in pesan_asli or "timed out" in pesan_asli:
        return "Database tidak menjawab. Kemungkinan internet lambat atau terputus."
    elif "Connection refused" in pesan_asli or "server closed the connection" in pesan_asli:
        return "Database menolak atau memutus sambungan. Tunggu sebentar lalu klik Muat ulang."
    elif "Network is unreachable" in pesan_asli:
        return "Jaringan tidak terjangkau. Pastikan memakai connection string Session pooler."
    else:
        return "Database bermasalah. Pesan aslinya: " + pesan_asli


def baca_tabel(perintah_sql, parameter=None):
    """
    Menjalankan satu perintah SELECT dan mengembalikan hasilnya sebagai tabel pandas.
    Kalau hasilnya kosong, tetap dikembalikan tabel kosong lengkap dengan nama kolomnya.
    """
    if not file_env_ada():
        raise DatabaseGagal("File .env tidak ditemukan. Salin .env.example menjadi .env, lalu isi.")

    database_url = ambil_pengaturan(DATABASE_URL)
    if database_url == "":
        raise DatabaseGagal("DATABASE_URL di file .env masih kosong.")

    try:
        with psycopg.connect(database_url, connect_timeout=BATAS_TUNGGU_DETIK) as koneksi:
            with koneksi.cursor(row_factory=dict_row) as kursor:
                kursor.execute(perintah_sql, parameter)
                semua_baris = kursor.fetchall()
                nama_kolom = []
                for kolom in kursor.description:
                    nama_kolom.append(kolom.name)
    except psycopg.Error as error:
        raise DatabaseGagal(terjemahkan_error(str(error)))

    return pd.DataFrame(semua_baris, columns=nama_kolom)


# ---------------------------------------------------------------------
# Untuk halaman Kelurahan
# ---------------------------------------------------------------------

def ambil_antrean():
    """
    Semua pengajuan dari view antrean_kelurahan, dengan urutan sesuai kontrak data:
    skor tertinggi dulu, lalu tenggat terdekat, lalu yang masuk lebih dulu.
    Kolom waktu sudah diubah ke jam Jakarta dalam bentuk teks.
    """
    perintah_sql = """
        select *,
               to_char(dibuat_pada at time zone 'Asia/Jakarta', 'DD-MM HH24:MI') as waktu_masuk
        from antrean_kelurahan
        order by skor_prioritas desc, tenggat_program asc nulls last, dibuat_pada asc
    """
    return baca_tabel(perintah_sql)


def ambil_jejak_perubahan():
    """
    Satu baris kecil untuk mendeteksi ada data baru atau berubah:
    jumlah pengajuan dan waktu perubahan terakhir. Dipakai untuk penyegaran otomatis.
    """
    perintah_sql = """
        select count(*) as jumlah,
               coalesce(max(diperbarui_pada)::text, '-') as terakhir_berubah
        from pengajuan
    """
    tabel = baca_tabel(perintah_sql)
    baris = tabel.iloc[0]
    return str(baris["jumlah"]) + "|" + str(baris["terakhir_berubah"])


def ambil_detail_pengajuan(kode_pengajuan):
    """Kolom tambahan satu pengajuan yang tidak ada di view antrean."""
    perintah_sql = """
        select kecamatan, jenjang_anak, usia_sasaran, ada_lansia, ada_disabilitas,
               desil_menurut_warga, desil_sebelumnya_menurut_warga, nama_petugas,
               to_char(batas_tindak_lanjut at time zone 'Asia/Jakarta', 'DD-MM HH24:MI') as batas_tindak_lanjut,
               to_char(telegram_terhubung_pada at time zone 'Asia/Jakarta', 'DD-MM HH24:MI') as telegram_terhubung_pada
        from pengajuan
        where kode_pengajuan = %s
    """
    tabel = baca_tabel(perintah_sql, [kode_pengajuan])
    if len(tabel) == 0:
        return None
    return tabel.iloc[0]


def ambil_riwayat_pesan(kode_pengajuan):
    """Pesan Telegram yang sudah dikirim untuk satu pengajuan, terbaru di atas."""
    perintah_sql = """
        select to_char(dikirim_pada at time zone 'Asia/Jakarta', 'DD-MM HH24:MI:SS') as waktu,
               workflow, jenis, penerima, berhasil, pesan_error
        from log_notifikasi
        where kode_pengajuan = %s
        order by dikirim_pada desc
        limit 20
    """
    return baca_tabel(perintah_sql, [kode_pengajuan])


# ---------------------------------------------------------------------
# Untuk halaman Warga
# ---------------------------------------------------------------------

def ambil_aturan_program():
    """Semua program aktif dari tabel aturan_program."""
    perintah_sql = """
        select kode_program, nama_program, kelompok_sasaran, jenjang_berlaku,
               usia_min, usia_max, min_lama_domisili_tahun, desil_maks,
               tanggal_buka, tanggal_tutup, keterangan_jadwal,
               langkah_pengajuan, berkas_wajib,
               sumber_judul, sumber_tautan, sumber_tanggal_akses, adalah_contoh
        from aturan_program
        where aktif = true
        order by kode_program
    """
    return baca_tabel(perintah_sql)


def ambil_persona():
    """Tokoh demonstrasi (adalah_persona = true) dari tabel rumah_tangga."""
    perintah_sql = """
        select id, nama_perwakilan, kelurahan, kecamatan, jenjang_anak, usia_anak,
               ada_lansia, ada_disabilitas, lama_domisili_tahun,
               desil_menurut_warga, desil_sebelumnya_menurut_warga, catatan
        from rumah_tangga
        where adalah_persona = true
        order by id
    """
    return baca_tabel(perintah_sql)
