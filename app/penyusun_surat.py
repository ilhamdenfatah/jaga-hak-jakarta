"""
Penyusun berkas: surat permohonan, daftar berkas, dan kronologi dalam satu file Word.

Semua isi disusun dari templat tetap dan isian warga. Tidak ada AI di file ini,
jadi isinya bisa diperiksa dan selalu sama untuk isian yang sama.

Surat ditujukan kepada Lurah, berisi permohonan pendampingan dan verifikasi berkas
supaya pengajuan dapat diteruskan ke dinas terkait. Keputusan tetap di dinas.

Tidak ada isian NIK, nomor KK, nomor HP, atau alamat lengkap, dan memang tidak boleh ditambahkan.
"""

import io
import re
from datetime import date

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

import pemeriksa_program as pp


NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

TEKS_PENANDA_SIMULASI = (
    "CONTOH DOKUMEN SIMULASI. Disusun otomatis di stan Jaga Hak Jakarta, PPKD Jakarta Barat. "
    "Dokumen ini tidak dikirim ke kelurahan, dinas, atau sistem resmi pemerintah mana pun."
)

BIRU = RGBColor(0x1B, 0x3F, 0xA6)
ABU = RGBColor(0x6B, 0x6B, 0x6B)


# ---------------------------------------------------------------------
# Bantuan kecil
# ---------------------------------------------------------------------

def tanggal_indonesia(tanggal):
    """date(2026, 10, 16) menjadi '16 Oktober 2026'."""
    return str(tanggal.day) + " " + NAMA_BULAN[tanggal.month - 1] + " " + str(tanggal.year)


def isi_atau_strip(teks):
    if pp.kosong(teks):
        return "-"
    return str(teks)


def daftar_berkas_lengkap(program):
    """
    Berkas dari tabel aturan. Kalau program terkendala desil dan tangkapan layar
    Cek Bansos belum ada di daftar, ditambahkan di akhir.
    """
    daftar = list(program["berkas"])
    if program["hasil"] == pp.HASIL_TERKENDALA:
        sudah_ada = False
        for berkas in daftar:
            if "cek bansos" in berkas.lower():
                sudah_ada = True
        if not sudah_ada:
            daftar.append("Tangkapan layar hasil Cek Bansos")
    return daftar


def nama_file(isian, program):
    """Contoh: 'Pengajuan_KJP_PLUS_Bu_Lia.docx'. Hanya huruf, angka, dan garis bawah."""
    nama = isian["nama_pemohon"] or "warga"
    nama = re.sub(r"[^A-Za-z0-9]+", "_", nama).strip("_")
    if nama == "":
        nama = "warga"
    return "Pengajuan_" + program["kode_program"] + "_" + nama[:30] + ".docx"


# ---------------------------------------------------------------------
# Isi dokumen
# ---------------------------------------------------------------------

def kronologi_contoh(isian, program):
    """
    Kronologi siap pakai untuk tokoh demonstrasi, supaya demo tidak menunggu pengunjung mengetik.
    Disusun dari isian, tanpa AI. Pengunjung tetap bisa mengubahnya.
    """
    kalimat = []

    if pp.desil_naik(isian):
        kalimat.append(
            "Saat saya memeriksa aplikasi Cek Bansos, desil keluarga kami tercatat naik dari "
            + str(isian["desil_sebelumnya_menurut_warga"]) + " menjadi "
            + str(isian["desil_menurut_warga"]) + ", padahal menurut kami kondisi keluarga tidak berubah."
        )

    jenjang = isian["jenjang_anak"]
    if jenjang in pp.JENJANG_SEKOLAH:
        kalimat.append("Anak kami saat ini bersekolah di jenjang " + jenjang + ".")
    elif jenjang == "PT":
        kalimat.append("Anak kami saat ini sedang kuliah.")
    elif jenjang == "PAUD":
        kalimat.append("Anak kami masih berusia dini.")

    if isian["ada_lansia"]:
        kalimat.append("Di rumah kami ada anggota keluarga lansia.")
    if isian["ada_disabilitas"]:
        kalimat.append("Di rumah kami ada anggota keluarga penyandang disabilitas.")

    kalimat.append(
        "Kami khawatir tidak dapat mengikuti " + program["nama_program"]
        + " dan mohon pendampingan kelurahan agar berkas kami lengkap sebelum diteruskan."
    )
    return " ".join(kalimat)


def paragraf_isi_surat(isian, program):
    """Paragraf inti surat permohonan, dipakai di Word dan di pratinjau layar."""
    paragraf = []
    paragraf.append(
        "Dengan ini saya mengajukan permohonan pendampingan dan verifikasi berkas untuk pengajuan "
        + program["nama_program"] + ", agar berkas saya dapat diperiksa kelengkapannya dan "
        "diteruskan kepada dinas terkait."
    )

    if pp.desil_naik(isian) or program["hasil"] == pp.HASIL_TERKENDALA:
        teks = "Sebagai keterangan, "
        if pp.desil_naik(isian):
            teks = (teks + "desil keluarga kami yang tercantum di aplikasi Cek Bansos berubah dari "
                    + str(isian["desil_sebelumnya_menurut_warga"]) + " menjadi "
                    + str(isian["desil_menurut_warga"]) + ". ")
        else:
            teks = (teks + "desil keluarga kami yang tercantum di aplikasi Cek Bansos adalah "
                    + str(isian["desil_menurut_warga"]) + ". ")
        teks = teks + ("Kami juga memohon arahan mengenai usul sanggah data melalui jalur resmi, "
                       "bila data tersebut tidak sesuai dengan kondisi kami.")
        paragraf.append(teks)

    paragraf.append(
        "Bersama surat ini saya sampaikan kronologi singkat dan daftar berkas sebagaimana terlampir. "
        "Saya bersedia melengkapi berkas lain bila diperlukan."
    )
    paragraf.append("Demikian permohonan ini saya sampaikan. Atas perhatian dan bantuan Bapak/Ibu Lurah, "
                    "saya ucapkan terima kasih.")
    return paragraf


def tambah_paragraf(dokumen, teks, tebal=False, ukuran=11, warna=None, rata=None, jarak_bawah=6):
    paragraf = dokumen.add_paragraph()
    potongan = paragraf.add_run(teks)
    potongan.bold = tebal
    potongan.font.size = Pt(ukuran)
    if warna is not None:
        potongan.font.color.rgb = warna
    if rata is not None:
        paragraf.alignment = rata
    paragraf.paragraph_format.space_after = Pt(jarak_bawah)
    return paragraf


def buat_docx(isian, program, kronologi, tanggal=None):
    """Membuat file Word berisi surat, daftar berkas, dan kronologi. Hasilnya bytes siap diunduh."""
    if tanggal is None:
        tanggal = date.today()

    dokumen = Document()
    gaya = dokumen.styles["Normal"]
    gaya.font.name = "Arial"
    gaya.font.size = Pt(11)

    # Penanda simulasi di bagian atas
    tambah_paragraf(dokumen, TEKS_PENANDA_SIMULASI, ukuran=8, warna=ABU, jarak_bawah=18)

    # ----- Bagian 1: surat permohonan -----
    tambah_paragraf(dokumen, "Jakarta, " + tanggal_indonesia(tanggal), rata=WD_ALIGN_PARAGRAPH.RIGHT)

    tambah_paragraf(dokumen, "Kepada Yth.", jarak_bawah=0)
    tambah_paragraf(dokumen, "Lurah " + isi_atau_strip(isian["kelurahan"]), jarak_bawah=0)
    tambah_paragraf(dokumen, "Kecamatan " + isi_atau_strip(isian["kecamatan"]), jarak_bawah=0)
    tambah_paragraf(dokumen, "di Jakarta", jarak_bawah=12)

    tambah_paragraf(dokumen, "Perihal: Permohonan pendampingan pengajuan " + program["nama_program"],
                    tebal=True, jarak_bawah=12)

    tambah_paragraf(dokumen, "Dengan hormat,")
    tambah_paragraf(dokumen, "Saya yang bertanda tangan di bawah ini:", jarak_bawah=2)

    tabel_identitas = dokumen.add_table(rows=0, cols=2)
    baris_identitas = [
        ("Nama", isi_atau_strip(isian["nama_pemohon"])),
        ("Kelurahan", isi_atau_strip(isian["kelurahan"])),
        ("Kecamatan", isi_atau_strip(isian["kecamatan"])),
        ("Program yang diajukan", program["nama_program"]),
    ]
    for label, nilai in baris_identitas:
        sel = tabel_identitas.add_row().cells
        sel[0].text = label
        sel[1].text = ": " + nilai
    dokumen.add_paragraph()

    for teks in paragraf_isi_surat(isian, program):
        tambah_paragraf(dokumen, teks, rata=WD_ALIGN_PARAGRAPH.JUSTIFY)

    tambah_paragraf(dokumen, "Hormat saya,", jarak_bawah=40)
    tambah_paragraf(dokumen, isi_atau_strip(isian["nama_pemohon"]))

    # ----- Bagian 2: daftar berkas -----
    dokumen.add_page_break()
    tambah_paragraf(dokumen, "Lampiran 1. Daftar berkas yang perlu dibawa ke kelurahan",
                    tebal=True, ukuran=13, warna=BIRU, jarak_bawah=4)
    # Di dokumen dipakai tanggal pasti, bukan "sekian hari lagi", supaya tidak basi saat dibuka besok
    if program["tanggal_tutup"] is not None:
        teks_jadwal = "Batas pendaftaran: " + tanggal_indonesia(program["tanggal_tutup"]) + "."
    else:
        teks_jadwal = program["jadwal"] + "."
    tambah_paragraf(dokumen, "Program: " + program["nama_program"] + ". " + teks_jadwal, jarak_bawah=10)

    daftar = daftar_berkas_lengkap(program)
    if len(daftar) == 0:
        tambah_paragraf(dokumen, "Daftar berkas belum tercatat untuk program ini. Tanyakan kepada petugas kelurahan.")
    else:
        tabel_berkas = dokumen.add_table(rows=1, cols=3)
        tabel_berkas.style = "Table Grid"
        judul = tabel_berkas.rows[0].cells
        judul[0].text = "No"
        judul[1].text = "Berkas"
        judul[2].text = "Sudah disiapkan"
        nomor = 0
        for berkas in daftar:
            nomor = nomor + 1
            sel = tabel_berkas.add_row().cells
            sel[0].text = str(nomor)
            sel[1].text = berkas
            sel[2].text = ""

        # Lebar kolom: No sempit, Berkas lebar
        lebar_kolom = [Cm(1.2), Cm(10.5), Cm(4.3)]
        tabel_berkas.autofit = False
        for nomor_kolom in range(3):
            tabel_berkas.columns[nomor_kolom].width = lebar_kolom[nomor_kolom]
        for baris in tabel_berkas.rows:
            for nomor_kolom in range(3):
                baris.cells[nomor_kolom].width = lebar_kolom[nomor_kolom]

    if not pp.kosong(program["langkah"]):
        tambah_paragraf(dokumen, "")
        tambah_paragraf(dokumen, "Langkah pengajuan menurut sumber resmi:", tebal=True, jarak_bawah=2)
        tambah_paragraf(dokumen, str(program["langkah"]))

    teks_sumber = "Sumber aturan: " + isi_atau_strip(program["sumber_judul"])
    if not pp.kosong(program["sumber_tautan"]):
        teks_sumber = teks_sumber + " (" + str(program["sumber_tautan"]) + ")"
    tambah_paragraf(dokumen, teks_sumber, ukuran=9, warna=ABU)
    if program["adalah_contoh"]:
        tambah_paragraf(dokumen, "Aturan program di atas adalah data contoh untuk uji coba, bukan aturan resmi.",
                        ukuran=9, warna=ABU)

    # ----- Bagian 3: kronologi -----
    dokumen.add_page_break()
    tambah_paragraf(dokumen, "Lampiran 2. Kronologi singkat", tebal=True, ukuran=13, warna=BIRU, jarak_bawah=4)
    tambah_paragraf(dokumen, "Ditulis oleh pemohon dengan kata-kata sendiri.", ukuran=9, warna=ABU, jarak_bawah=10)
    for baris in kronologi.strip().split("\n"):
        if baris.strip() != "":
            tambah_paragraf(dokumen, baris.strip(), rata=WD_ALIGN_PARAGRAPH.JUSTIFY)

    tambah_paragraf(dokumen, "")
    tambah_paragraf(dokumen, "Hasil pemeriksaan program di stan berbunyi \"dapat diajukan\", bukan jaminan diterima. "
                    "Keputusan penerima bantuan ada di instansi berwenang.", ukuran=9, warna=ABU)

    # Simpan ke memori, bukan ke folder, lalu kembalikan isinya
    wadah = io.BytesIO()
    dokumen.save(wadah)
    return wadah.getvalue()
