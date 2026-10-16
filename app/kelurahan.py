"""
Halaman Kelurahan: meja petugas (PC 2).

Isi halaman, dari atas ke bawah:
1. Ringkasan angka.
2. Tabel antrean, urut berdasarkan skor prioritas.
3. Detail satu pengajuan dan formulir ubah status.

Halaman ini hanya MEMBACA dari database. Tombol simpan status mengirim data ke n8n (W2),
lalu n8n yang menyimpan ke database dan mengabari warga lewat Telegram.
"""

from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

import db
import webhook
from pengaturan import DAFTAR_STATUS, TEKS_SIMULASI


# Jam Jakarta (WIB) tanpa perlu paket zona waktu tambahan di Windows
WIB = timezone(timedelta(hours=7))

# Seberapa sering halaman mengecek data baru (detik)
JEDA_CEK_DATA_BARU = 10

NAMA_PETUGAS_BAWAAN = "Petugas Kelurahan (contoh)"


st.set_page_config(page_title="Meja Petugas Kelurahan", layout="wide")


# ---------------------------------------------------------------------
# Bantuan kecil untuk tampilan
# ---------------------------------------------------------------------

def adalah_benar(nilai):
    """Benar hanya kalau nilainya ya/true. Kosong (NULL) dianggap tidak."""
    if nilai is None or pd.isna(nilai):
        return False
    return bool(nilai)


def teks_ya_tidak(nilai):
    if adalah_benar(nilai):
        return "Ya"
    else:
        return "-"


def teks_tenggat(baris):
    """Contoh hasil: 'Tenggat dekat (2 hari lagi)', 'Lewat tenggat', '30-10-2026', atau '-'."""
    tanggal = baris["tenggat_program"]
    if tanggal is None or pd.isna(tanggal):
        return "-"

    sisa_hari = int(baris["sisa_hari_tenggat"])
    tanda = baris["tanda_tenggat"]

    if tanda == "Lewat tenggat":
        return "Lewat tenggat"
    elif tanda == "Tenggat dekat":
        if sisa_hari == 0:
            return "Tenggat dekat (hari ini)"
        else:
            return "Tenggat dekat (" + str(sisa_hari) + " hari lagi)"
    else:
        return tanggal.strftime("%d-%m-%Y")


def susun_tabel_tampil(antrean):
    """Mengubah data antrean menjadi tabel yang enak dibaca petugas."""
    semua_baris = []
    for _, baris in antrean.iterrows():
        if adalah_benar(baris["lewat_batas_tindak_lanjut"]):
            keterangan_batas = "Terlambat"
        else:
            keterangan_batas = "-"

        semua_baris.append({
            "Kode": baris["kode_pengajuan"],
            "Pemohon": baris["nama_pemohon"],
            "Kelurahan": baris["kelurahan"],
            "Program": baris["nama_program"],
            "Prioritas": baris["kategori_prioritas"] + " (" + str(baris["skor_prioritas"]) + ")",
            "Tenggat": teks_tenggat(baris),
            "Rentan": teks_ya_tidak(baris["kelompok_rentan"]),
            "Status": baris["status"],
            "Tindak lanjut": keterangan_batas,
            "Telegram": teks_ya_tidak(baris["telegram_terhubung"]),
            "Masuk": baris["waktu_masuk"],
            "Sumber": baris["sumber_data"],
        })
    return pd.DataFrame(semua_baris)


def warna_prioritas(nilai):
    """Warna teks kolom Prioritas: Tinggi oranye, Sedang biru."""
    if str(nilai).startswith("Tinggi"):
        return "color: #F2672E; font-weight: 600"
    elif str(nilai).startswith("Sedang"):
        return "color: #1B3FA6"
    else:
        return ""


def label_pilihan(kode, antrean):
    """Teks di daftar pilihan, contoh: 'JHJ0001  |  Bu Lia  |  KJP Plus  |  Tinggi'."""
    baris = antrean[antrean["kode_pengajuan"] == kode].iloc[0]
    return (kode + "  |  " + baris["nama_pemohon"] + "  |  " + baris["nama_program"]
            + "  |  " + baris["kategori_prioritas"])


# ---------------------------------------------------------------------
# Penyegaran otomatis
# Setiap beberapa detik, bagian kecil ini mengecek apakah ada pengajuan baru
# atau perubahan data. Kalau ada, seluruh halaman dimuat ulang.
# Kalau tidak ada, halaman dibiarkan, supaya petugas yang sedang mengetik tidak terganggu.
# ---------------------------------------------------------------------

@st.fragment(run_every=JEDA_CEK_DATA_BARU)
def pantau_data_baru():
    try:
        jejak_baru = db.ambil_jejak_perubahan()
    except db.DatabaseGagal as error:
        st.caption("Gagal mengecek data baru: " + str(error))
        return

    jam_sekarang = datetime.now(WIB).strftime("%H:%M:%S")
    st.caption("Diperbarui otomatis. Terakhir dicek pukul " + jam_sekarang + " WIB.")

    if jejak_baru != st.session_state.get("jejak_data"):
        st.rerun(scope="app")


# ---------------------------------------------------------------------
# Bagian atas: judul
# ---------------------------------------------------------------------

kolom_judul, kolom_segar = st.columns([4, 1])
with kolom_judul:
    st.title("Meja Petugas Kelurahan")
    st.caption(TEKS_SIMULASI)
with kolom_segar:
    st.write("")
    if st.button("Muat ulang", width="stretch"):
        st.rerun()


# ---------------------------------------------------------------------
# Ambil data. Kalau database bermasalah, tampilkan pesan dan berhenti di sini.
# ---------------------------------------------------------------------

try:
    st.session_state["jejak_data"] = db.ambil_jejak_perubahan()
    antrean = db.ambil_antrean()
except db.DatabaseGagal as error:
    st.error("Data antrean belum bisa dimuat. " + str(error))
    st.stop()

with kolom_segar:
    pantau_data_baru()


# ---------------------------------------------------------------------
# 1. Ringkasan angka
# ---------------------------------------------------------------------

jumlah_total = len(antrean)
jumlah_belum_ditangani = 0
jumlah_tinggi_belum_ditangani = 0
jumlah_terlambat = 0

for _, baris in antrean.iterrows():
    if baris["status"] == "Diterima":
        jumlah_belum_ditangani = jumlah_belum_ditangani + 1
        if baris["kategori_prioritas"] == "Tinggi":
            jumlah_tinggi_belum_ditangani = jumlah_tinggi_belum_ditangani + 1
    if adalah_benar(baris["lewat_batas_tindak_lanjut"]):
        jumlah_terlambat = jumlah_terlambat + 1

kolom1, kolom2, kolom3, kolom4 = st.columns(4)
kolom1.metric("Total pengajuan", jumlah_total, border=True)
kolom2.metric("Belum ditangani", jumlah_belum_ditangani, border=True,
              help="Pengajuan berstatus Diterima.")
kolom3.metric("Prioritas tinggi belum ditangani", jumlah_tinggi_belum_ditangani, border=True,
              help="Skor 50 ke atas: tenggat program sangat dekat atau ada kelompok rentan.")
kolom4.metric("Terlambat ditindaklanjuti", jumlah_terlambat, border=True,
              help="Masih berstatus Diterima padahal batas waktu tindak lanjut sudah lewat.")


# ---------------------------------------------------------------------
# 2. Tabel antrean
# ---------------------------------------------------------------------

st.subheader("Antrean pengajuan")

pilihan_tampil = st.radio(
    "Tampilkan",
    ["Semua", "Belum ditangani", "Sudah diproses"],
    horizontal=True,
    label_visibility="collapsed",
)

if pilihan_tampil == "Belum ditangani":
    antrean_tampil = antrean[antrean["status"] == "Diterima"]
elif pilihan_tampil == "Sudah diproses":
    antrean_tampil = antrean[antrean["status"] != "Diterima"]
else:
    antrean_tampil = antrean

if len(antrean_tampil) == 0:
    st.info("Belum ada pengajuan di kelompok ini.")
    st.stop()

tabel_tampil = susun_tabel_tampil(antrean_tampil)
st.dataframe(
    tabel_tampil.style.map(warna_prioritas, subset=["Prioritas"]),
    hide_index=True,
    width="stretch",
)
st.caption(
    "Urutan dihitung otomatis dari tenggat program dan kelompok rentan (lansia atau disabilitas), "
    "dengan rumus tetap tanpa AI. Kolom Sumber: stan = pengunjung, simulasi = data contoh, uji = percobaan tim."
)


# ---------------------------------------------------------------------
# 3. Detail dan ubah status
# ---------------------------------------------------------------------

st.subheader("Tindak lanjut pengajuan")

# Tampilkan hasil simpan dari klik sebelumnya (disimpan sebelum halaman dimuat ulang)
hasil_simpan = st.session_state.pop("hasil_simpan", None)
if hasil_simpan is not None:
    jenis_pesan, isi_pesan = hasil_simpan
    if jenis_pesan == "berhasil":
        st.success(isi_pesan)
    elif jenis_pesan == "peringatan":
        st.warning(isi_pesan)
    else:
        st.error(isi_pesan)

daftar_kode = list(antrean_tampil["kode_pengajuan"])

# Kalau pengajuan yang tadi dipilih sudah tidak ada di daftar (karena filter), kembali ke urutan teratas
if st.session_state.get("kode_terpilih") not in daftar_kode:
    st.session_state["kode_terpilih"] = daftar_kode[0]

kode_terpilih = st.selectbox(
    "Pilih pengajuan",
    daftar_kode,
    key="kode_terpilih",
    format_func=lambda kode: label_pilihan(kode, antrean),
)

baris = antrean[antrean["kode_pengajuan"] == kode_terpilih].iloc[0]

try:
    detail = db.ambil_detail_pengajuan(kode_terpilih)
    riwayat_pesan = db.ambil_riwayat_pesan(kode_terpilih)
except db.DatabaseGagal as error:
    st.error("Detail pengajuan belum bisa dimuat. " + str(error))
    st.stop()

if detail is None:
    st.warning("Pengajuan ini tidak ditemukan lagi di database. Klik Muat ulang.")
    st.stop()

kolom_detail, kolom_form = st.columns([3, 2], gap="large")

with kolom_detail:
    st.markdown("**" + baris["nama_pemohon"] + "**, Kelurahan " + baris["kelurahan"])

    kecamatan = detail["kecamatan"]
    if kecamatan is None or pd.isna(kecamatan):
        kecamatan = "-"

    desil_sekarang = detail["desil_menurut_warga"]
    desil_sebelumnya = detail["desil_sebelumnya_menurut_warga"]
    if pd.isna(desil_sekarang):
        teks_desil = "Tidak diisi"
    elif pd.isna(desil_sebelumnya):
        teks_desil = str(int(desil_sekarang))
    else:
        teks_desil = str(int(desil_sebelumnya)) + " menjadi " + str(int(desil_sekarang))

    waktu_terhubung = detail["telegram_terhubung_pada"]
    if adalah_benar(baris["telegram_terhubung"]) and waktu_terhubung is not None and not pd.isna(waktu_terhubung):
        teks_telegram = "Terhubung sejak " + str(waktu_terhubung)
    elif adalah_benar(baris["telegram_terhubung"]):
        teks_telegram = "Terhubung"
    else:
        teks_telegram = "Belum terhubung"

    info = pd.DataFrame([
        {"Keterangan": "Kode pengajuan", "Isi": kode_terpilih},
        {"Keterangan": "Kecamatan", "Isi": kecamatan},
        {"Keterangan": "Program", "Isi": baris["nama_program"]},
        {"Keterangan": "Status saat ini", "Isi": baris["status"]},
        {"Keterangan": "Prioritas", "Isi": baris["kategori_prioritas"] + " (skor " + str(baris["skor_prioritas"]) + ")"},
        {"Keterangan": "Tenggat program", "Isi": teks_tenggat(baris)},
        {"Keterangan": "Ada lansia", "Isi": teks_ya_tidak(detail["ada_lansia"])},
        {"Keterangan": "Ada penyandang disabilitas", "Isi": teks_ya_tidak(detail["ada_disabilitas"])},
        {"Keterangan": "Desil menurut warga", "Isi": teks_desil},
        {"Keterangan": "Masuk", "Isi": baris["waktu_masuk"]},
        {"Keterangan": "Batas tindak lanjut", "Isi": str(detail["batas_tindak_lanjut"])},
        {"Keterangan": "Telegram warga", "Isi": teks_telegram},
    ])
    # Tinggi tabel disesuaikan jumlah baris supaya tidak perlu digulir
    st.dataframe(info, hide_index=True, width="stretch", height=(len(info) + 1) * 35 + 3)

    st.markdown("**Kronologi dari warga**")
    st.write(baris["kronologi"])

    ringkasan = baris["ringkasan_ai"]
    if ringkasan is not None and not pd.isna(ringkasan) and str(ringkasan).strip() != "":
        st.markdown("**Ringkasan otomatis**")
        st.caption("Disusun AI hanya untuk membantu membaca. Bukan dasar keputusan.")
        st.write(ringkasan)

with kolom_form:
    if not adalah_benar(baris["telegram_terhubung"]):
        st.info("Warga belum menghubungkan Telegram. Status tetap tersimpan, "
                "tetapi kabar tidak bisa dikirim ke warga.")

    with st.form("form_ubah_status"):
        status_lama = baris["status"]
        status_baru = st.selectbox(
            "Status baru",
            DAFTAR_STATUS,
            index=DAFTAR_STATUS.index(status_lama),
            key="status_baru_" + kode_terpilih,
        )
        catatan = st.text_area(
            "Catatan untuk warga (boleh kosong)",
            key="catatan_" + kode_terpilih,
            help="Catatan ini ikut dikirim ke warga lewat Telegram.",
        )
        nama_petugas = st.text_input("Nama petugas", value=NAMA_PETUGAS_BAWAAN,
                                     key="nama_petugas_" + kode_terpilih)
        tombol_simpan = st.form_submit_button("Simpan dan kabari warga", type="primary",
                                              width="stretch")

    if tombol_simpan:
        if status_baru == status_lama and catatan.strip() == "":
            st.warning("Status belum diubah dan catatan kosong. Tidak ada yang dikirim.")
        else:
            with st.spinner("Mengirim ke n8n..."):
                hasil = webhook.kirim_perubahan_status(kode_terpilih, status_baru, catatan, nama_petugas)

            if hasil["ok"] and hasil.get("notifikasi_terkirim") is True:
                st.session_state["hasil_simpan"] = (
                    "berhasil",
                    "Status " + kode_terpilih + " tersimpan: " + status_baru + ". Kabar sudah dikirim ke Telegram warga.",
                )
            elif hasil["ok"]:
                st.session_state["hasil_simpan"] = (
                    "peringatan",
                    "Status " + kode_terpilih + " tersimpan: " + status_baru + ". " + hasil["pesan"],
                )
            else:
                st.session_state["hasil_simpan"] = ("gagal", hasil["pesan"])

            # Kosongkan catatan kalau sudah tersimpan, lalu muat ulang supaya tabel ikut berubah
            if hasil["ok"]:
                st.session_state.pop("catatan_" + kode_terpilih, None)
            st.rerun()

    st.markdown("**Riwayat pesan Telegram**")
    if len(riwayat_pesan) == 0:
        st.caption("Belum ada pesan untuk pengajuan ini.")
    else:
        riwayat_tampil = []
        for _, pesan in riwayat_pesan.iterrows():
            if adalah_benar(pesan["berhasil"]):
                hasil_kirim = "Terkirim"
            else:
                hasil_kirim = "Gagal"
            riwayat_tampil.append({
                "Waktu": pesan["waktu"],
                "Dari": pesan["workflow"],
                "Jenis": pesan["jenis"],
                "Kepada": pesan["penerima"],
                "Hasil": hasil_kirim,
            })
        st.dataframe(pd.DataFrame(riwayat_tampil), hide_index=True, width="stretch")
