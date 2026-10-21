"""
Jawaban cadangan untuk pertanyaan demo utama.

Dipakai HANYA kalau Groq tidak bisa dihubungi (internet putus, kena batas pemakaian,
atau kunci bermasalah), supaya demo di depan pejabat tetap berjalan.

Setiap jawaban ditulis tangan dari dokumen di data/dokumen_bersih/ dan menyebut
file sumbernya. Kalau dokumen sumber berubah, periksa ulang jawaban di sini.

Cara mencocokkan: pertanyaan cocok dengan satu cadangan kalau memuat SEMUA kata
dalam salah satu kelompok "kata_kunci". Daftar diperiksa dari atas ke bawah,
jadi cadangan yang lebih spesifik ditaruh di atas.
"""

import re

DAFTAR_CADANGAN = [
    {
        "nama": "desil 6 dan KJP Plus",
        "kata_kunci": [["kjp", "desil"]],
        "jawaban": (
            "Menurut Peraturan Gubernur Nomor 20 Tahun 2026 Pasal 17 ayat (4), verifikasi kelayakan "
            "bantuan sosial biaya pendidikan didasarkan pada peringkat kesejahteraan desil 1 sampai desil 5, "
            "sesuai kemampuan keuangan daerah. Calon penerima baru KJP Plus diperingkatkan mulai dari desil "
            "terendah sesuai kuota anggaran. Penerima lanjutan tetap dapat menerima sampai lulus jenjang "
            "pendidikan sepanjang masih memenuhi persyaratan.\n\n"
            "Kalau Bapak atau Ibu merasa desil keluarga tidak sesuai kondisi sebenarnya, usul atau sanggah "
            "data dapat diajukan melalui aplikasi Cek Bansos, operator SIKS-NG di kelurahan, atau Cek DTSEN BPS. "
            "Pengajuan tidak otomatis mengubah desil, dan keputusan penerima ada di Dinas Pendidikan."
        ),
        "sumber_file": [
            "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt",
            "persyaratan_kjp_plus_tahap_ii_2026.txt",
            "bps_arti_desil_dtsen_2026.txt",
        ],
    },
    {
        "nama": "memperbaiki data desil",
        "kata_kunci": [["usul"], ["sanggah"], ["perbaiki"], ["memperbaiki"], ["perbaikan"],
                       ["pembaruan"], ["memperbarui"], ["desil", "salah"], ["desil", "sesuai"]],
        "jawaban": (
            "Kalau status desil keluarga dirasa tidak sesuai, usulan pembaruan data dapat diajukan melalui:\n"
            "- aplikasi Cek Bansos Kemensos (cekbansos.kemensos.go.id),\n"
            "- Cek DTSEN BPS (dtsen-form.bps.go.id), atau\n"
            "- petugas pendata dan pendamping sosial di kelurahan (operator SIKS-NG).\n\n"
            "Usulan diteruskan ke BPS untuk pemeringkatan nasional, jadi prosesnya butuh waktu. Pengajuan tidak "
            "otomatis menurunkan desil: hasil akhirnya bisa lebih rendah, tetap, atau lebih tinggi."
        ),
        "sumber_file": ["siladu_faq_dtsen_dan_bansos_dki.txt", "bps_arti_desil_dtsen_2026.txt"],
    },
    {
        "nama": "kenapa desil berubah",
        "kata_kunci": [["desil", "naik"], ["desil", "turun"], ["desil", "berubah"], ["apa", "itu", "desil"],
                       ["arti", "desil"]],
        "jawaban": (
            "Menurut BPS, desil adalah posisi relatif kesejahteraan sebuah keluarga dibandingkan keluarga lain, "
            "dari desil 1 (paling rendah) sampai desil 10. Desil bukan ukuran pendapatan. Desil dihitung dari "
            "banyak hal sekaligus, misalnya kondisi rumah, aset, listrik, pendidikan, dan pekerjaan.\n\n"
            "Desil bisa berubah karena kondisi keluarga berubah, atau karena posisi keluarga tersebut "
            "dibandingkan keluarga lain berubah saat data dimutakhirkan. Kalau dirasa tidak sesuai, usul atau "
            "sanggah dapat diajukan melalui Cek Bansos, operator SIKS-NG di kelurahan, atau Cek DTSEN BPS. "
            "Pengajuan tidak otomatis mengubah desil."
        ),
        "sumber_file": ["bps_arti_desil_dtsen_2026.txt", "siladu_faq_dtsen_dan_bansos_dki.txt"],
    },
    {
        "nama": "syarat KJMU",
        "kata_kunci": [["kjmu", "syarat"], ["kjmu", "persyaratan"], ["kjmu", "kriteria"], ["kjmu", "daftar"],
                       ["kjmu", "pendaftaran"], ["kjmu", "kapan"], ["kjmu", "pengumuman"],
                       ["kjmu", "cair"], ["kjmu", "jadwal"]],
        "jawaban": (
            "Kriteria calon penerima baru KJMU menurut juknis Dinas Pendidikan (Kepdis 505/2026), antara lain:\n"
            "- NIK DKI Jakarta dan berdomisili di Jakarta paling singkat 5 tahun berturut-turut;\n"
            "- terdaftar dalam DTSEN atau penerima manfaat panti sosial;\n"
            "- lulus pendidikan menengah (SMA, SMK, sederajat, atau Sekolah Rakyat) paling lama 3 tahun terakhir;\n"
            "- diterima di PTN jalur reguler, atau PTS jalur reguler dengan akreditasi paling rendah C atau Baik;\n"
            "- pengajuan paling lambat semester 4;\n"
            "- indeks prestasi semester paling rendah 2,75 (PTN) atau 3,00 (PTS), kecuali mahasiswa semester 1 "
            "dan penyandang disabilitas.\n\n"
            "Pendaftaran KJMU Tahap II 2026 dibuka 30 September dan diperpanjang sampai 11 Oktober 2026, "
            "jadi sudah ditutup. Menurut timeline terbaru P4OP, penetapan penerima melalui Keputusan Gubernur "
            "dijadwalkan 22 sampai 29 Oktober 2026 dan penyaluran dana 30 Oktober 2026. Silakan pantau pengumuman "
            "resmi di p4op.jakarta.go.id/kjmu atau Instagram @upt.p4op."
        ),
        "sumber_file": ["kepdis_505_2026_juknis_kjmu.txt", "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"],
    },
    {
        "nama": "syarat KJP Plus",
        "kata_kunci": [["kjp", "syarat"], ["kjp", "persyaratan"], ["kjp", "kriteria"], ["kjp", "daftar"],
                       ["kjp", "pendaftaran"], ["kjp", "kapan"]],
        "jawaban": (
            "Persyaratan penerima KJP Plus menurut infografis Dinas Pendidikan:\n"
            "1. Memiliki NIK sebagai penduduk DKI Jakarta.\n"
            "2. Berdomisili di DKI Jakarta paling singkat 5 tahun berturut-turut.\n"
            "3. Berusia 6 sampai 21 tahun.\n"
            "4. Terdaftar sebagai murid di sekolah negeri atau swasta di DKI Jakarta.\n"
            "5. Terdaftar dalam DTSEN atau penerima manfaat panti sosial.\n\n"
            "Pendataan KJP Plus Tahap II 2026 (pendaftaran melalui sekolah 24 Juli sampai 5 Agustus 2026) "
            "sudah selesai. Silakan pantau pengumuman resmi di edu.jakarta.go.id/kjp."
        ),
        "sumber_file": ["persyaratan_kjp_plus_tahap_ii_2026.txt", "timeline_kjp_plus_tahap_ii_2026.txt"],
    },
    {
        "nama": "kontak P4OP",
        "kata_kunci": [["kontak"], ["whatsapp"], ["wa"], ["hubungi"], ["pengaduan"], ["telepon"]],
        "jawaban": (
            "Layanan informasi dan pengaduan KJP Plus dan KJMU (P4OP Dinas Pendidikan DKI Jakarta):\n"
            "- WhatsApp: 0852-1124-7089\n"
            "- Telepon: 021-3528-9335\n"
            "- Alamat: Jl. Budi Utomo No. 3, Pasar Baru, Sawah Besar, Jakarta Pusat\n"
            "- Jam layanan: 08.00 sampai 16.00 WIB pada hari kerja\n"
            "- Instagram: @upt.p4op"
        ),
        "sumber_file": ["kontak_p4op.txt"],
    },
]


def ubah_jadi_kata(teks):
    teks = teks.lower()
    teks = re.sub(r"[^a-z0-9]+", " ", teks)
    return set(teks.split())


def cari_cadangan(pertanyaan):
    """Mengembalikan cadangan pertama yang cocok, atau None."""
    kata_pertanyaan = ubah_jadi_kata(pertanyaan)
    for cadangan in DAFTAR_CADANGAN:
        for kelompok in cadangan["kata_kunci"]:
            semua_ada = True
            for kata in kelompok:
                if kata not in kata_pertanyaan:
                    semua_ada = False
                    break
            if semua_ada:
                return cadangan
    return None
