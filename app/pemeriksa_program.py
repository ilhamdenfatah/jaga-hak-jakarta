"""
Pemeriksa program: mencocokkan isian warga dengan tabel aturan_program.

Tidak ada AI di file ini. Hasilnya ditentukan sepenuhnya oleh aturan tertulis,
jadi isian yang sama selalu memberi hasil yang sama.

Setiap program yang relevan mendapat salah satu dari tiga hasil:
    HASIL_DAPAT          : "Dapat diajukan"
    HASIL_TERKENDALA     : "Dapat diajukan, terkendala desil"
    HASIL_BELUM_SESUAI   : "Belum sesuai"

Kata yang dipakai selalu "dapat diajukan", bukan "berhak".
Keputusan penerima bantuan ada di instansi berwenang.

Program yang kelompok sasarannya tidak ada di rumah warga (misalnya program lansia
untuk keluarga tanpa lansia) tidak ditampilkan sama sekali, supaya hasilnya tidak ramai.
"""

from datetime import date

import pandas as pd


HASIL_DAPAT = "Dapat diajukan"
HASIL_TERKENDALA = "Dapat diajukan, terkendala desil"
HASIL_BELUM_SESUAI = "Belum sesuai"

# Urutan tampil hasil
URUTAN_HASIL = [HASIL_DAPAT, HASIL_TERKENDALA, HASIL_BELUM_SESUAI]

# Pilihan jenjang di formulir. Kiri: teks yang dilihat warga. Kanan: kode yang disimpan.
PILIHAN_JENJANG = {
    "Tidak ada yang sekolah atau kuliah": None,
    "Belum sekolah (usia dini)": "PAUD",
    "SD": "SD",
    "SMP": "SMP",
    "SMA": "SMA",
    "SMK": "SMK",
    "Perguruan tinggi": "PT",
}

JENJANG_SEKOLAH = ["SD", "SMP", "SMA", "SMK"]


def kosong(nilai):
    """Benar kalau nilai tidak diisi (None, NaN, atau teks kosong)."""
    if nilai is None:
        return True
    if isinstance(nilai, str):
        return nilai.strip() == ""
    try:
        return bool(pd.isna(nilai))
    except (TypeError, ValueError):
        return False


def format_tanggal(tanggal):
    """date menjadi teks 'DD-MM-YYYY'."""
    return tanggal.strftime("%d-%m-%Y")


def pecah_daftar(teks, pemisah):
    """'Kartu Keluarga; Kartu pelajar' menjadi ['Kartu Keluarga', 'Kartu pelajar']."""
    if kosong(teks):
        return []
    hasil = []
    for bagian in str(teks).split(pemisah):
        bagian = bagian.strip()
        if bagian != "":
            hasil.append(bagian)
    return hasil


def program_relevan(aturan, isian):
    """
    Apakah program ini menyasar seseorang di rumah warga?
    Kalau tidak, program tidak ditampilkan sama sekali.
    """
    kelompok = aturan["kelompok_sasaran"]
    jenjang = isian["jenjang_anak"]

    if kelompok == "siswa":
        return jenjang in JENJANG_SEKOLAH
    elif kelompok == "mahasiswa":
        return jenjang == "PT"
    elif kelompok == "anak_usia_dini":
        return jenjang == "PAUD"
    elif kelompok == "lansia":
        return isian["ada_lansia"] is True
    elif kelompok == "disabilitas":
        return isian["ada_disabilitas"] is True
    elif kelompok == "keluarga":
        return True
    else:
        return False


def teks_jadwal(aturan, hari_ini):
    """Contoh hasil: 'Ditutup 30-10-2026 (14 hari lagi)'."""
    tanggal_buka = aturan["tanggal_buka"]
    tanggal_tutup = aturan["tanggal_tutup"]

    if kosong(tanggal_tutup):
        if not kosong(aturan["keterangan_jadwal"]):
            return str(aturan["keterangan_jadwal"])
        return "Jadwal belum tercatat"

    sisa_hari = (tanggal_tutup - hari_ini).days
    if sisa_hari < 0:
        teks = "Sudah ditutup " + format_tanggal(tanggal_tutup)
    elif sisa_hari == 0:
        teks = "Ditutup hari ini, " + format_tanggal(tanggal_tutup)
    else:
        teks = "Ditutup " + format_tanggal(tanggal_tutup) + " (" + str(sisa_hari) + " hari lagi)"

    if not kosong(tanggal_buka) and tanggal_buka > hari_ini:
        teks = "Dibuka " + format_tanggal(tanggal_buka) + ". " + teks
    return teks


def periksa_satu_program(aturan, isian, hari_ini):
    """
    Memeriksa satu baris aturan_program terhadap isian warga.
    Hasilnya dict berisi hasil, alasan (kenapa belum sesuai atau terkendala),
    dan catatan (hal yang perlu diperhatikan warga).
    """
    alasan = []
    catatan = []

    # Langkah 1: syarat jenjang
    daftar_jenjang = pecah_daftar(aturan["jenjang_berlaku"], ",")
    if len(daftar_jenjang) > 0 and isian["jenjang_anak"] not in daftar_jenjang:
        alasan.append("Program ini untuk jenjang " + ", ".join(daftar_jenjang) + ".")

    # Langkah 2: syarat usia orang yang dibantu
    usia = isian["usia_sasaran"]
    usia_min = aturan["usia_min"]
    usia_max = aturan["usia_max"]
    if not kosong(usia_min) or not kosong(usia_max):
        if kosong(usia):
            catatan.append("Usia orang yang dibantu belum diisi, jadi syarat usia belum diperiksa.")
        else:
            if not kosong(usia_min) and usia < int(usia_min):
                alasan.append("Usia minimal " + str(int(usia_min)) + " tahun.")
            if not kosong(usia_max) and usia > int(usia_max):
                alasan.append("Usia maksimal " + str(int(usia_max)) + " tahun.")

    # Langkah 3: syarat lama tinggal di Jakarta
    minimal_domisili = aturan["min_lama_domisili_tahun"]
    lama_domisili = isian["lama_domisili_tahun"]
    if not kosong(minimal_domisili):
        if kosong(lama_domisili):
            catatan.append("Lama tinggal di Jakarta belum diisi, jadi syarat domisili belum diperiksa.")
        elif lama_domisili < int(minimal_domisili):
            alasan.append("Minimal tinggal di Jakarta " + str(int(minimal_domisili)) + " tahun.")

    # Langkah 4: jadwal pendaftaran
    tanggal_tutup = aturan["tanggal_tutup"]
    tanggal_buka = aturan["tanggal_buka"]
    if not kosong(tanggal_tutup) and tanggal_tutup < hari_ini:
        alasan.append("Pendaftaran sudah ditutup pada " + format_tanggal(tanggal_tutup) + ".")
    elif not kosong(tanggal_buka) and tanggal_buka > hari_ini:
        catatan.append("Pendaftaran baru dibuka " + format_tanggal(tanggal_buka)
                       + ". Berkas bisa disiapkan dari sekarang.")

    # Kalau ada syarat selain desil yang tidak cocok, hasilnya "Belum sesuai"
    if len(alasan) > 0:
        return {"hasil": HASIL_BELUM_SESUAI, "alasan": alasan, "catatan": catatan}

    # Langkah 5: desil. Sistem hanya membandingkan angka yang dilihat warga sendiri,
    # tidak menghitung atau menilai desil.
    desil_maks = aturan["desil_maks"]
    desil_warga = isian["desil_menurut_warga"]
    if not kosong(desil_maks):
        if kosong(desil_warga):
            catatan.append("Desil belum diisi. Program ini mensyaratkan desil paling tinggi "
                           + str(int(desil_maks)) + ". Cek desil keluarga di aplikasi Cek Bansos.")
        elif desil_warga > int(desil_maks):
            alasan.append("Desil yang Anda lihat di Cek Bansos (" + str(desil_warga)
                          + ") di atas batas program (" + str(int(desil_maks)) + ").")
            return {"hasil": HASIL_TERKENDALA, "alasan": alasan, "catatan": catatan}

    return {"hasil": HASIL_DAPAT, "alasan": alasan, "catatan": catatan}


def susun_hasil(aturan, pemeriksaan, hari_ini):
    """Menggabungkan baris aturan dan hasil pemeriksaan menjadi satu dict untuk ditampilkan."""
    tanggal_tutup = aturan["tanggal_tutup"]
    if kosong(tanggal_tutup):
        tanggal_tutup = None

    return {
        "kode_program": aturan["kode_program"],
        "nama_program": aturan["nama_program"],
        "hasil": pemeriksaan["hasil"],
        "alasan": pemeriksaan["alasan"],
        "catatan": pemeriksaan["catatan"],
        "jadwal": teks_jadwal(aturan, hari_ini),
        "tanggal_tutup": tanggal_tutup,
        "langkah": aturan["langkah_pengajuan"],
        "berkas": pecah_daftar(aturan["berkas_wajib"], ";"),
        "sumber_judul": aturan["sumber_judul"],
        "sumber_tautan": aturan["sumber_tautan"],
        "sumber_tanggal_akses": aturan["sumber_tanggal_akses"],
        "adalah_contoh": bool(aturan["adalah_contoh"]),
    }


def kunci_urut(hasil):
    """Urutan tampil: kelompok hasil dulu, lalu tenggat terdekat (yang tanpa tenggat di bawah)."""
    nomor_kelompok = URUTAN_HASIL.index(hasil["hasil"])
    if hasil["tanggal_tutup"] is None:
        tanggal = date(9999, 12, 31)
    else:
        tanggal = hasil["tanggal_tutup"]
    return (nomor_kelompok, tanggal, hasil["nama_program"])


def periksa_semua_program(tabel_aturan, isian, hari_ini=None):
    """
    Memeriksa semua program di tabel_aturan (yang dibaca hanya program aktif).

    Hasilnya dict berisi dua bagian:
        program          : program bantuan yang relevan, sudah diurutkan
        jalur_perbaikan  : program berkelompok "keluarga" (misalnya usul sanggah di Cek Bansos).
                           Hanya diisi kalau desil yang dilihat warga naik, atau ada program
                           yang terkendala desil. Selain itu daftar kosong.
    """
    if hari_ini is None:
        hari_ini = date.today()

    daftar_program = []
    daftar_jalur = []

    for _, aturan in tabel_aturan.iterrows():
        if not program_relevan(aturan, isian):
            continue

        pemeriksaan = periksa_satu_program(aturan, isian, hari_ini)
        hasil = susun_hasil(aturan, pemeriksaan, hari_ini)

        if aturan["kelompok_sasaran"] == "keluarga":
            daftar_jalur.append(hasil)
        else:
            daftar_program.append(hasil)

    daftar_program.sort(key=kunci_urut)
    daftar_jalur.sort(key=kunci_urut)

    # Jalur perbaikan data hanya ditampilkan kalau memang ada alasannya
    ada_terkendala = False
    for hasil in daftar_program:
        if hasil["hasil"] == HASIL_TERKENDALA:
            ada_terkendala = True

    if not desil_naik(isian) and not ada_terkendala:
        daftar_jalur = []

    return {"program": daftar_program, "jalur_perbaikan": daftar_jalur}


def desil_naik(isian):
    """Benar kalau desil yang dilihat warga sekarang lebih tinggi dari sebelumnya."""
    sekarang = isian["desil_menurut_warga"]
    sebelumnya = isian["desil_sebelumnya_menurut_warga"]
    if kosong(sekarang) or kosong(sebelumnya):
        return False
    return sekarang > sebelumnya
