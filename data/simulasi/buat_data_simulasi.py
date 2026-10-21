"""
Generator data simulasi Jaga Hak Jakarta.

Script ini TIDAK terhubung ke database. Hasilnya dua file SQL di folder yang sama:
  01_persona.sql        4 tokoh demonstrasi (adalah_persona = true)
  02_data_simulasi.sql  296 rumah tangga simulasi + 50 pengajuan simulasi

Semua nama, wilayah RT/RW, dan cerita di sini FIKTIF. Tidak ada NIK, KK,
nomor HP, atau alamat lengkap. Aturan pengisian mengikuti kontrak_data.md bagian 12.

Acakan memakai angka awal tetap (BENIH_ACAK), jadi hasilnya selalu sama
setiap kali script dijalankan.
"""

import os
import random

BENIH_ACAK = 2026
JUMLAH_RUMAH_TANGGA = 296      # ditambah 4 persona = 300
PENANDA_SIMULASI = "Data simulasi"
NAMA_PETUGAS = "Petugas Kelurahan (contoh)"

FOLDER_INI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------
# 1. Wilayah Jakarta Barat: 8 kecamatan, 56 kelurahan
# ---------------------------------------------------------------------
WILAYAH = {
    "Cengkareng": ["Cengkareng Barat", "Cengkareng Timur", "Duri Kosambi", "Kapuk",
                   "Kedaung Kali Angke", "Rawa Buaya"],
    "Grogol Petamburan": ["Grogol", "Jelambar", "Jelambar Baru", "Tanjung Duren Selatan",
                          "Tanjung Duren Utara", "Tomang", "Wijaya Kusuma"],
    "Taman Sari": ["Glodok", "Keagungan", "Krukut", "Mangga Besar", "Maphar",
                   "Pinangsia", "Taman Sari", "Tangki"],
    "Tambora": ["Angke", "Duri Selatan", "Duri Utara", "Jembatan Besi", "Jembatan Lima",
                "Kali Anyar", "Krendang", "Pekojan", "Roa Malaka", "Tambora", "Tanah Sereal"],
    "Kebon Jeruk": ["Duri Kepa", "Kebon Jeruk", "Kedoya Selatan", "Kedoya Utara",
                    "Kelapa Dua", "Sukabumi Selatan", "Sukabumi Utara"],
    "Kalideres": ["Kalideres", "Kamal", "Pegadungan", "Semanan", "Tegal Alur"],
    "Palmerah": ["Jatipulo", "Kemanggisan", "Kota Bambu Selatan", "Kota Bambu Utara",
                 "Palmerah", "Slipi"],
    "Kembangan": ["Joglo", "Kembangan Selatan", "Kembangan Utara", "Meruya Selatan",
                  "Meruya Utara", "Srengseng"],
}


# ---------------------------------------------------------------------
# 2. Nama fiktif. Sengaja tanpa Lia, Siti, Dewi, Ratna (dipakai persona)
#    dan tanpa kombinasi yang mirip nama tokoh publik.
# ---------------------------------------------------------------------
NAMA_DEPAN_PEREMPUAN = ["Sri", "Rina", "Yuni", "Nur", "Ani", "Tuti", "Wati", "Endang",
                        "Rini", "Eka", "Fitri", "Indah", "Maya", "Novi", "Ratih", "Sari",
                        "Yanti", "Dian", "Heni", "Lilis", "Nining", "Atik", "Rohani",
                        "Suryani", "Juariah", "Masitoh", "Komariah", "Nurhayati",
                        "Rukmini", "Sumarni", "Ernawati", "Hartini"]
NAMA_BELAKANG_PEREMPUAN = ["Handayani", "Wulandari", "Rahayu", "Susanti", "Purwanti",
                           "Kurniasih", "Maryati", "Setiawati", "Lestari", "Anggraeni",
                           "Fauziah", "Hasanah"]
NAMA_DEPAN_LAKI = ["Joko", "Budi", "Agus", "Slamet", "Hendra", "Dedi", "Rudi", "Bambang",
                   "Sutrisno", "Yusuf", "Rahmat", "Asep", "Ujang", "Iwan", "Teguh", "Eko",
                   "Hasan", "Ahmad", "Dani", "Supri", "Wahyu", "Andi", "Rizal", "Fajar",
                   "Ridwan", "Mulyadi", "Sugeng", "Haris", "Tono", "Darto"]
NAMA_BELAKANG_LAKI = ["Santoso", "Prasetyo", "Hidayat", "Saputra", "Kurniawan",
                      "Setiawan", "Nugroho", "Wibowo", "Hermawan", "Firmansyah",
                      "Ramadhan", "Hakim"]


# ---------------------------------------------------------------------
# 3. Persona demonstrasi (keputusan 20-21 Okt)
#    Bu Lia sama persis dengan data uji Streamlit.
# ---------------------------------------------------------------------
PERSONA = [
    {
        "nama_perwakilan": "Bu Lia", "kelurahan": "Kedoya Utara", "kecamatan": "Kebon Jeruk",
        "rw": "004", "rt": "007", "jumlah_anggota": 4,
        "jenjang_anak": "SMP", "usia_anak": 14, "ada_lansia": False, "ada_disabilitas": False,
        "lama_domisili_tahun": 12, "desil_menurut_warga": 6, "desil_sebelumnya_menurut_warga": 4,
        "catatan": "Tokoh utama demonstrasi. Anak kelas 9 SMP. Desil keluarga naik dari 4 "
                   "menjadi 6 sehingga terancam tidak mendapat KJP Plus.",
    },
    {
        "nama_perwakilan": "Bu Siti", "kelurahan": "Cengkareng Timur", "kecamatan": "Cengkareng",
        "rw": "009", "rt": "003", "jumlah_anggota": 3,
        "jenjang_anak": "SMP", "usia_anak": 13, "ada_lansia": False, "ada_disabilitas": False,
        "lama_domisili_tahun": 9, "desil_menurut_warga": 5, "desil_sebelumnya_menurut_warga": 3,
        "catatan": "Ibu tunggal, buruh cuci dengan penghasilan tidak tetap. Anak kelas VIII SMP "
                   "sebelumnya menerima KJP Plus. Desil naik dari 3 menjadi 5.",
    },
    {
        "nama_perwakilan": "Bu Dewi", "kelurahan": "Tegal Alur", "kecamatan": "Kalideres",
        "rw": "011", "rt": "005", "jumlah_anggota": 4,
        "jenjang_anak": "SMA", "usia_anak": 16, "ada_lansia": False, "ada_disabilitas": False,
        "lama_domisili_tahun": 15, "desil_menurut_warga": 7, "desil_sebelumnya_menurut_warga": 7,
        "catatan": "Suami terkena PHK empat bulan lalu dan kini bekerja harian. Data kesejahteraan "
                   "diduga masih menggambarkan keadaan sebelum PHK. Anak kelas XI SMA.",
    },
    {
        "nama_perwakilan": "Bu Ratna", "kelurahan": "Meruya Utara", "kecamatan": "Kembangan",
        "rw": "002", "rt": "010", "jumlah_anggota": 4,
        "jenjang_anak": "PT", "usia_anak": 18, "ada_lansia": True, "ada_disabilitas": False,
        "lama_domisili_tahun": 18, "desil_menurut_warga": 4, "desil_sebelumnya_menurut_warga": 4,
        "catatan": "Ibu dari Aisyah (18), baru lulus SMA dan ingin kuliah. Tinggal bersama adik "
                   "Aisyah dan nenek. Alamat ayah di dokumen kependudukan berbeda dari tempat "
                   "tinggal keluarga.",
    },
]


# ---------------------------------------------------------------------
# 4. Fungsi bantu penulisan SQL
# ---------------------------------------------------------------------
def teks_sql(nilai):
    """Mengubah nilai Python menjadi tulisan SQL yang aman."""
    if nilai is None:
        return "null"
    if nilai is True:
        return "true"
    if nilai is False:
        return "false"
    if isinstance(nilai, int):
        return str(nilai)
    # Tanda kutip tunggal di dalam teks digandakan supaya SQL tidak rusak
    return "'" + str(nilai).replace("'", "''") + "'"


def waktu_lalu(menit):
    """Waktu sekian menit sebelum perintah dijalankan, dalam bentuk SQL."""
    return "now() - interval '" + str(menit) + " minutes'"


# ---------------------------------------------------------------------
# 5. Membuat satu rumah tangga simulasi
# ---------------------------------------------------------------------
def buat_nama(nama_terpakai):
    """Nama fiktif dengan sapaan Bu atau Pak, tidak boleh dobel."""
    while True:
        if random.random() < 0.7:
            nama = ("Bu " + random.choice(NAMA_DEPAN_PEREMPUAN) + " "
                    + random.choice(NAMA_BELAKANG_PEREMPUAN))
        else:
            nama = ("Pak " + random.choice(NAMA_DEPAN_LAKI) + " "
                    + random.choice(NAMA_BELAKANG_LAKI))
        if nama not in nama_terpakai:
            nama_terpakai.add(nama)
            return nama


def buat_jenjang_dan_usia():
    """Jenjang anak utama dan usianya. Kadang tidak ada anak usia sekolah."""
    angka = random.random()
    if angka < 0.30:
        return "SD", random.randint(7, 12)
    elif angka < 0.50:
        return "SMP", random.randint(13, 15)
    elif angka < 0.62:
        return "SMA", random.randint(16, 18)
    elif angka < 0.72:
        return "SMK", random.randint(16, 18)
    elif angka < 0.80:
        return "PT", random.randint(18, 23)
    elif angka < 0.88:
        return "PAUD", random.randint(3, 6)
    else:
        return None, None


def buat_desil():
    """Desil yang dilihat warga di Cek Bansos, sekarang dan sebelumnya. Bukan hitungan sistem."""
    if random.random() < 0.05:
        return None, None   # warga belum pernah memeriksa desilnya

    bobot = [10, 12, 13, 13, 12, 11, 10, 8, 6, 5]
    desil_sekarang = random.choices(range(1, 11), weights=bobot)[0]

    angka = random.random()
    if angka < 0.60:
        desil_sebelumnya = desil_sekarang                          # tidak berubah
    elif angka < 0.85:
        desil_sebelumnya = desil_sekarang - random.randint(1, 3)   # desil naik
    else:
        desil_sebelumnya = desil_sekarang + random.randint(1, 2)   # desil turun

    if desil_sebelumnya < 1:
        desil_sebelumnya = 1
    if desil_sebelumnya > 10:
        desil_sebelumnya = 10
    return desil_sekarang, desil_sebelumnya


def buat_rumah_tangga(nama_terpakai):
    kecamatan = random.choice(list(WILAYAH.keys()))
    kelurahan = random.choice(WILAYAH[kecamatan])
    jenjang, usia = buat_jenjang_dan_usia()
    desil_sekarang, desil_sebelumnya = buat_desil()
    ada_lansia = random.random() < 0.25
    ada_disabilitas = random.random() < 0.08

    jumlah_anggota = random.randint(2, 6)
    if ada_lansia:
        jumlah_anggota = jumlah_anggota + 1

    return {
        "nama_perwakilan": buat_nama(nama_terpakai),
        "kelurahan": kelurahan,
        "kecamatan": kecamatan,
        "rw": str(random.randint(1, 12)).zfill(3),
        "rt": str(random.randint(1, 15)).zfill(3),
        "jumlah_anggota": jumlah_anggota,
        "jenjang_anak": jenjang,
        "usia_anak": usia,
        "ada_lansia": ada_lansia,
        "ada_disabilitas": ada_disabilitas,
        "lama_domisili_tahun": random.randint(1, 35),
        "desil_menurut_warga": desil_sekarang,
        "desil_sebelumnya_menurut_warga": desil_sebelumnya,
        "catatan": PENANDA_SIMULASI,
    }


# ---------------------------------------------------------------------
# 6. Pengajuan simulasi
# ---------------------------------------------------------------------
# Jumlah pengajuan per program, total 50.
# KJMU sedikit dan dibuat sebelum tenggat contoh (6 Okt), sehingga bertanda "Lewat tenggat".
TARGET_PROGRAM = (["KJP_PLUS"] * 25 + ["KLJ"] * 8 + ["KAJ"] * 5 + ["USUL_SANGGAH"] * 5
                  + ["KPDJ"] * 4 + ["KJMU"] * 3)

# Sebaran status, total 50
TARGET_STATUS = (["Diterima"] * 16 + ["Sedang diverifikasi"] * 14
                 + ["Perlu berkas tambahan"] * 8 + ["Diteruskan ke dinas"] * 12)

CATATAN_PETUGAS = {
    "Sedang diverifikasi": [
        "Berkas sedang dicocokkan dengan data kelurahan.",
        "Petugas sedang mengonfirmasi domisili ke pengurus RT setempat.",
        None,
    ],
    "Perlu berkas tambahan": [
        "Mohon lengkapi fotokopi Kartu Keluarga terbaru.",
        "Mohon bawa surat keterangan aktif dari sekolah.",
        "Mohon lampirkan tangkapan layar hasil Cek Bansos, ya.",
        "Mohon bawa surat keterangan dari tempat kerja sebelumnya.",
    ],
    "Diteruskan ke dinas": [
        "Berkas lengkap dan sudah diteruskan ke dinas terkait.",
        "Sudah diteruskan ke dinas terkait. Keputusan ada di dinas.",
    ],
}

# Kalimat pembuka kronologi, dipisah untuk perwakilan perempuan (Bu) dan laki-laki (Pak)
KALIMAT_KEADAAN_BU = [
    "Penghasilan keluarga kami tidak tetap karena saya bekerja serabutan.",
    "Suami saya terkena PHK beberapa bulan lalu dan sekarang bekerja harian.",
    "Saya mengurus anak-anak sendiri dan bekerja sebagai buruh cuci.",
    "Usaha warung kami sepi sejak awal tahun.",
    "Kami tinggal di rumah kontrakan dan pengeluaran bulanan makin berat.",
    "Suami saya pengemudi ojek daring dengan pendapatan yang berubah-ubah.",
    "Saya berjualan makanan kecil dengan penghasilan sekitar satu juta rupiah per bulan.",
]
KALIMAT_KEADAAN_PAK = [
    "Penghasilan keluarga kami tidak tetap karena saya bekerja serabutan.",
    "Saya terkena PHK beberapa bulan lalu dan sekarang bekerja harian.",
    "Saya buruh bangunan dan pekerjaan tidak selalu ada setiap minggu.",
    "Usaha warung kami sepi sejak awal tahun.",
    "Kami tinggal di rumah kontrakan dan pengeluaran bulanan makin berat.",
    "Saya pengemudi ojek daring dengan pendapatan yang berubah-ubah.",
]


def cocok_dengan_program(rt, kode_program):
    """Rumah tangga ini punya sasaran untuk program tersebut atau tidak."""
    if kode_program == "KJP_PLUS":
        return rt["jenjang_anak"] in ["SD", "SMP", "SMA", "SMK"]
    elif kode_program == "KJMU":
        return rt["jenjang_anak"] == "PT"
    elif kode_program == "KAJ":
        return rt["jenjang_anak"] == "PAUD"
    elif kode_program == "KLJ":
        return rt["ada_lansia"]
    elif kode_program == "KPDJ":
        return rt["ada_disabilitas"]
    elif kode_program == "USUL_SANGGAH":
        return (rt["desil_menurut_warga"] is not None
                and rt["desil_menurut_warga"] > rt["desil_sebelumnya_menurut_warga"])
    return False


def buat_kronologi(rt, kode_program):
    if rt["nama_perwakilan"].startswith("Pak "):
        kalimat = [random.choice(KALIMAT_KEADAAN_PAK)]
    else:
        kalimat = [random.choice(KALIMAT_KEADAAN_BU)]

    desil = rt["desil_menurut_warga"]
    desil_lama = rt["desil_sebelumnya_menurut_warga"]
    if desil is not None and desil > desil_lama:
        kalimat.append("Di Cek Bansos desil keluarga kami naik dari " + str(desil_lama)
                       + " menjadi " + str(desil) + ", padahal keadaan kami tidak membaik.")

    if kode_program == "KJP_PLUS":
        kalimat.append("Anak kami bersekolah di jenjang " + rt["jenjang_anak"]
                       + " dan kami ingin mengajukan KJP Plus.")
    elif kode_program == "KJMU":
        kalimat.append("Anak kami kuliah dan kami ingin mengajukan KJMU.")
    elif kode_program == "KAJ":
        kalimat.append("Anak kami masih usia dini dan kami ingin mengajukan Kartu Anak Jakarta.")
    elif kode_program == "KLJ":
        kalimat.append("Orang tua kami yang sudah lansia tinggal bersama kami. "
                       "Kami ingin mengajukan Kartu Lansia Jakarta.")
    elif kode_program == "KPDJ":
        kalimat.append("Ada anggota keluarga kami penyandang disabilitas. "
                       "Kami ingin mengajukan Kartu Penyandang Disabilitas Jakarta.")
    elif kode_program == "USUL_SANGGAH":
        kalimat.append("Kami ingin dibantu menyiapkan usul sanggah data.")

    kalimat.append("Mohon pendampingan kelurahan untuk memeriksa berkas kami.")
    return " ".join(kalimat)


def usia_sasaran(rt, kode_program):
    if kode_program in ["KJP_PLUS", "KJMU", "KAJ"]:
        return rt["usia_anak"]
    elif kode_program == "KLJ":
        return random.randint(60, 84)
    return None


def buat_waktu(status, kode_program, nomor_diterima):
    """
    Mengembalikan (dibuat, pengingat, batas, diperbarui) dalam MENIT yang lalu.
    Angka negatif berarti di masa depan.

    - Pengajuan Diterima kebanyakan baru masuk (2-40 jam lalu) dengan pengingat 3 hari
      dan batas 5 hari, supaya sampai 23 Okt tidak menumpuk tanda "lewat batas".
      Tiga yang pertama sengaja lama (3-6 hari lalu, batas 2 hari) untuk contoh lewat batas.
    - Status lain: masuk 1-14 hari lalu, pengingat 1 hari, batas 2 hari, diubah petugas
      2-48 jam setelah masuk.
    - KJMU: masuk 15-20 hari lalu, sebelum tenggat contoh 6 Okt.
    """
    satu_jam = 60
    satu_hari = 24 * satu_jam

    if kode_program == "KJMU":
        dibuat = random.randint(15 * satu_hari, 20 * satu_hari)
    elif status == "Diterima" and nomor_diterima < 3:
        dibuat = random.randint(3 * satu_hari, 6 * satu_hari)
    elif status == "Diterima":
        dibuat = random.randint(2 * satu_jam, 40 * satu_jam)
    else:
        dibuat = random.randint(1 * satu_hari, 14 * satu_hari)

    if status == "Diterima" and nomor_diterima >= 3:
        pengingat = dibuat - 3 * satu_hari
        batas = dibuat - 5 * satu_hari
    else:
        pengingat = dibuat - 1 * satu_hari
        batas = dibuat - 2 * satu_hari

    if status == "Diterima":
        diperbarui = dibuat
    else:
        diperbarui = dibuat - random.randint(2 * satu_jam, 48 * satu_jam)
        if diperbarui < 30:
            diperbarui = 30   # perubahan status paling lambat 30 menit lalu, tidak di masa depan

    return dibuat, pengingat, batas, diperbarui


def buat_pengajuan(daftar_rumah_tangga):
    status_acak = TARGET_STATUS[:]
    random.shuffle(status_acak)

    # KJMU tidak boleh berstatus Diterima (sudah lama masuk). Tukar dengan status lain.
    for i in range(len(TARGET_PROGRAM)):
        if TARGET_PROGRAM[i] == "KJMU" and status_acak[i] == "Diterima":
            for j in range(len(status_acak)):
                if TARGET_PROGRAM[j] != "KJMU" and status_acak[j] != "Diterima":
                    status_acak[i], status_acak[j] = status_acak[j], status_acak[i]
                    break

    sudah_dipakai = set()
    hasil = []
    nomor_diterima = 0

    for i in range(len(TARGET_PROGRAM)):
        kode_program = TARGET_PROGRAM[i]
        status = status_acak[i]

        # Cari rumah tangga yang cocok dan belum dipakai
        calon = []
        for nomor in range(len(daftar_rumah_tangga)):
            rt = daftar_rumah_tangga[nomor]
            if nomor not in sudah_dipakai and cocok_dengan_program(rt, kode_program):
                calon.append(nomor)
        if len(calon) == 0:
            raise ValueError("Tidak ada rumah tangga yang cocok untuk " + kode_program)
        nomor_terpilih = random.choice(calon)
        sudah_dipakai.add(nomor_terpilih)
        rt = daftar_rumah_tangga[nomor_terpilih]

        dibuat, pengingat, batas, diperbarui = buat_waktu(status, kode_program, nomor_diterima)
        if status == "Diterima":
            nomor_diterima = nomor_diterima + 1

        catatan = None
        petugas = None
        if status != "Diterima":
            catatan = random.choice(CATATAN_PETUGAS[status])
            petugas = NAMA_PETUGAS

        hasil.append({
            "nama_pemohon": rt["nama_perwakilan"],
            "kelurahan": rt["kelurahan"],
            "kecamatan": rt["kecamatan"],
            "kode_program": kode_program,
            "jenjang_anak": rt["jenjang_anak"],
            "usia_sasaran": usia_sasaran(rt, kode_program),
            "ada_lansia": rt["ada_lansia"],
            "ada_disabilitas": rt["ada_disabilitas"],
            "desil_menurut_warga": rt["desil_menurut_warga"],
            "desil_sebelumnya_menurut_warga": rt["desil_sebelumnya_menurut_warga"],
            "kronologi": buat_kronologi(rt, kode_program),
            "status": status,
            "catatan_petugas": catatan,
            "nama_petugas": petugas,
            "menit_dibuat": dibuat,
            "menit_pengingat": pengingat,
            "menit_batas": batas,
            "menit_diperbarui": diperbarui,
        })

    # Urutkan dari yang paling lama, supaya nomor JHJ mengikuti urutan waktu masuk
    hasil.sort(key=lambda p: p["menit_dibuat"], reverse=True)
    return hasil


# ---------------------------------------------------------------------
# 7. Menulis file SQL
# ---------------------------------------------------------------------
KOLOM_RUMAH_TANGGA = ["nama_perwakilan", "kelurahan", "kecamatan", "rw", "rt", "jumlah_anggota",
                      "jenjang_anak", "usia_anak", "ada_lansia", "ada_disabilitas",
                      "lama_domisili_tahun", "desil_menurut_warga",
                      "desil_sebelumnya_menurut_warga", "catatan"]


def tulis_persona():
    baris = []
    baris.append("-- Jaga Hak Jakarta: 4 persona demonstrasi (fiktif)")
    baris.append("-- Dibuat oleh data/simulasi/buat_data_simulasi.py. Jalankan sekali di SQL Editor Supabase.")
    baris.append("-- Aman dijalankan ulang: tokoh yang sudah ada (nama sama, adalah_persona = true) dilewati.")
    baris.append("")
    for p in PERSONA:
        nilai = []
        for kolom in KOLOM_RUMAH_TANGGA:
            nilai.append(teks_sql(p[kolom]))
        baris.append("insert into rumah_tangga (" + ", ".join(KOLOM_RUMAH_TANGGA) + ", adalah_persona)")
        baris.append("select " + ", ".join(nilai) + ", true")
        baris.append("where not exists (select 1 from rumah_tangga where adalah_persona = true"
                     " and nama_perwakilan = " + teks_sql(p["nama_perwakilan"]) + ");")
        baris.append("")
    baris.append("-- Cek hasil: harus 4 baris")
    baris.append("select id, nama_perwakilan, kelurahan, jenjang_anak, desil_sebelumnya_menurut_warga,"
                 " desil_menurut_warga from rumah_tangga where adalah_persona = true order by id;")
    return "\n".join(baris) + "\n"


def tulis_data_simulasi(daftar_rumah_tangga, daftar_pengajuan):
    baris = []
    baris.append("-- Jaga Hak Jakarta: data simulasi (fiktif)")
    baris.append("-- " + str(len(daftar_rumah_tangga)) + " rumah tangga + "
                 + str(len(daftar_pengajuan)) + " pengajuan dengan sumber_data = 'simulasi'.")
    baris.append("-- Dibuat oleh data/simulasi/buat_data_simulasi.py. Jalankan sekali di SQL Editor Supabase.")
    baris.append("-- Kalau data simulasi sudah ada, perintah ini berhenti dan tidak mengisi apa pun.")
    baris.append("--")
    baris.append("-- Menghapus semua data simulasi (kalau perlu mengulang):")
    baris.append("--   delete from pengajuan where sumber_data = 'simulasi';")
    baris.append("--   delete from rumah_tangga where adalah_persona = false and catatan = '"
                 + PENANDA_SIMULASI + "';")
    baris.append("")
    baris.append("begin;")
    baris.append("")
    baris.append("do $$")
    baris.append("begin")
    baris.append("    if exists (select 1 from pengajuan where sumber_data = 'simulasi')")
    baris.append("       or exists (select 1 from rumah_tangga where catatan = '" + PENANDA_SIMULASI + "') then")
    baris.append("        raise exception 'Data simulasi sudah ada. Hapus dulu kalau ingin mengulang.';")
    baris.append("    end if;")
    baris.append("end $$;")
    baris.append("")

    # Rumah tangga
    baris.append("insert into rumah_tangga (" + ", ".join(KOLOM_RUMAH_TANGGA) + ") values")
    isi = []
    for rt in daftar_rumah_tangga:
        nilai = []
        for kolom in KOLOM_RUMAH_TANGGA:
            nilai.append(teks_sql(rt[kolom]))
        isi.append("(" + ", ".join(nilai) + ")")
    baris.append(",\n".join(isi) + ";")
    baris.append("")

    # Pengajuan. Tenggat diambil dari aturan_program saat perintah dijalankan.
    kolom_pengajuan = ["sumber_data", "nama_pemohon", "kelurahan", "kecamatan", "kode_program",
                       "jenjang_anak", "usia_sasaran", "ada_lansia", "ada_disabilitas",
                       "desil_menurut_warga", "desil_sebelumnya_menurut_warga", "tenggat_program",
                       "kronologi", "status", "catatan_petugas", "nama_petugas",
                       "dibuat_pada", "waktu_pengingat", "batas_tindak_lanjut", "diperbarui_pada"]
    baris.append("insert into pengajuan (" + ", ".join(kolom_pengajuan) + ") values")
    isi = []
    for p in daftar_pengajuan:
        tenggat = ("(select tanggal_tutup from aturan_program where kode_program = "
                   + teks_sql(p["kode_program"]) + ")")
        nilai = [
            "'simulasi'",
            teks_sql(p["nama_pemohon"]),
            teks_sql(p["kelurahan"]),
            teks_sql(p["kecamatan"]),
            teks_sql(p["kode_program"]),
            teks_sql(p["jenjang_anak"]),
            teks_sql(p["usia_sasaran"]),
            teks_sql(p["ada_lansia"]),
            teks_sql(p["ada_disabilitas"]),
            teks_sql(p["desil_menurut_warga"]),
            teks_sql(p["desil_sebelumnya_menurut_warga"]),
            tenggat,
            teks_sql(p["kronologi"]),
            teks_sql(p["status"]),
            teks_sql(p["catatan_petugas"]),
            teks_sql(p["nama_petugas"]),
            waktu_lalu(p["menit_dibuat"]),
            waktu_lalu(p["menit_pengingat"]),
            waktu_lalu(p["menit_batas"]),
            waktu_lalu(p["menit_diperbarui"]),
        ]
        isi.append("(" + ", ".join(nilai) + ")")
    baris.append(",\n".join(isi) + ";")
    baris.append("")
    baris.append("commit;")
    baris.append("")
    baris.append("-- Cek hasil: rumah tangga simulasi 296, pengajuan simulasi 50")
    baris.append("select (select count(*) from rumah_tangga where catatan = '" + PENANDA_SIMULASI
                 + "') as rumah_tangga_simulasi,")
    baris.append("       (select count(*) from pengajuan where sumber_data = 'simulasi') as pengajuan_simulasi;")
    return "\n".join(baris) + "\n"


def main():
    random.seed(BENIH_ACAK)

    nama_terpakai = set()
    daftar_rumah_tangga = []
    for nomor in range(JUMLAH_RUMAH_TANGGA):
        daftar_rumah_tangga.append(buat_rumah_tangga(nama_terpakai))

    daftar_pengajuan = buat_pengajuan(daftar_rumah_tangga)

    with open(os.path.join(FOLDER_INI, "01_persona.sql"), "w", encoding="utf-8") as berkas:
        berkas.write(tulis_persona())
    with open(os.path.join(FOLDER_INI, "02_data_simulasi.sql"), "w", encoding="utf-8") as berkas:
        berkas.write(tulis_data_simulasi(daftar_rumah_tangga, daftar_pengajuan))

    print("Selesai: 01_persona.sql (" + str(len(PERSONA)) + " persona) dan 02_data_simulasi.sql ("
          + str(len(daftar_rumah_tangga)) + " rumah tangga, " + str(len(daftar_pengajuan))
          + " pengajuan).")


if __name__ == "__main__":
    main()
