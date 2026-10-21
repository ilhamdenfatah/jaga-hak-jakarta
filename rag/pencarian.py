"""
Mencari potongan dokumen yang paling cocok dengan pertanyaan, memakai BM25.

BM25 bekerja seperti mencari di indeks buku: potongan yang memuat kata-kata
dari pertanyaan mendapat nilai lebih tinggi, terutama kata yang jarang muncul
(misalnya "KJMU" lebih bernilai daripada "bantuan"). Tidak memakai AI dan
tidak perlu mengunduh model apa pun.
"""

import math
import re

from rag.dokumen import muat_semua_potongan

# Angka pengatur BM25 yang umum dipakai
K1 = 1.5
B = 0.75

# Kata yang terlalu umum, diabaikan saat mencari
KATA_UMUM = {
    "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu", "atau", "pada",
    "dalam", "adalah", "akan", "juga", "tidak", "ada", "bisa", "dapat", "saya", "kami",
    "aku", "anda", "kita", "apa", "apakah", "bagaimana", "gimana", "kenapa", "mengapa",
    "berapa", "kapan", "siapa", "mana", "dimana", "tolong", "mohon", "bu", "pak", "ya",
    "nya", "sudah", "belum", "masih", "kalau", "jika", "agar", "supaya", "oleh", "sebagai",
    "tersebut", "para", "lain", "harus", "bisakah", "boleh", "mau", "ingin", "tentang",
    "jelaskan", "info", "informasi", "the", "sih", "dong", "kah", "lah", "per",
}

# Kata yang sering ditulis berbeda oleh warga. Kiri: tulisan warga. Kanan: kata tambahan yang dicari.
KATA_SEPADAN = {
    "kjp": ["kartu", "jakarta", "pintar", "peserta", "didik"],
    "kjmu": ["mahasiswa", "kartu", "jakarta", "unggul"],
    "klj": ["lansia", "lanjut", "usia"],
    "kaj": ["anak", "usia", "dini"],
    "kpdj": ["disabilitas", "penyandang"],
    "lansia": ["klj", "lanjut", "usia"],
    "disabilitas": ["kpdj", "penyandang"],
    "mahasiswa": ["kjmu"],
    "kuliah": ["mahasiswa", "kjmu", "perguruan", "tinggi"],
    "sekolah": ["peserta", "didik", "kjp"],
    "desil": ["kesejahteraan", "peringkat", "pemeringkatan"],
    "dtsen": ["desil", "data", "tunggal"],
    "sanggah": ["usul", "pembaruan", "perbaikan"],
    "perbaiki": ["usul", "sanggah", "pembaruan"],
    "memperbaiki": ["usul", "sanggah", "pembaruan"],
    "syarat": ["persyaratan", "kriteria"],
    "persyaratan": ["syarat", "kriteria"],
    "jadwal": ["tanggal", "pendaftaran", "timeline"],
    "daftar": ["pendaftaran", "pendataan"],
    "mendaftar": ["pendaftaran", "pendataan"],
    "kontak": ["whatsapp", "telepon", "pengaduan"],
    "hubungi": ["whatsapp", "telepon", "pengaduan"],
    "naik": ["berubah", "perubahan"],
    "turun": ["berubah", "perubahan"],
    "uang": ["besaran", "rp"],
    "berapa": ["besaran"],
    "ipk": ["indeks", "prestasi"],
    "ips": ["indeks", "prestasi"],
    "nilai": ["indeks", "prestasi"],
    "lolos": ["penetapan", "verifikasi", "seleksi"],
    "ditolak": ["penetapan", "verifikasi"],
    "pengumuman": ["penetapan"],
}


# Potongan penting yang wajib ikut kalau pertanyaan memuat kata tertentu.
# Dipakai untuk aturan kunci yang bahasanya jauh dari bahasa warga, sehingga BM25 sering melewatkannya.
# Format: (kata yang harus ada di pertanyaan, penggalan teks potongan, nama file)
POTONGAN_PENTING = [
    (["desil", "kjp"], "rentang desil 1 (satu) sampai desil 5",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    (["desil", "kjmu"], "rentang desil 1 (satu) sampai desil 5",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    (["desil", "sekolah"], "rentang desil 1 (satu) sampai desil 5",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    (["kjmu", "penetapan"], "verifikasi tahap kedua berdasarkan prestasi akademik",
     "kepdis_505_2026_juknis_kjmu.txt"),
    (["kjmu", "lolos"], "verifikasi tahap kedua berdasarkan prestasi akademik",
     "kepdis_505_2026_juknis_kjmu.txt"),
    (["kjmu", "ditolak"], "verifikasi tahap kedua berdasarkan prestasi akademik",
     "kepdis_505_2026_juknis_kjmu.txt"),
    # Larangan bagi penerima KJMU, termasuk bekerja penuh waktu (Pergub 20/2026 Pasal 20 ayat 2)
    (["kjmu", "bekerja"], "bekerja secara penuh waktu",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    (["kjmu", "kerja"], "bekerja secara penuh waktu",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    (["kjmu", "larangan"], "bekerja secara penuh waktu",
     "pergub_20_2026_bantuan_biaya_peningkatan_mutu_pendidikan.txt"),
    # Jadwal terbaru KJMU Tahap II (timeline P4OP)
    (["kjmu", "kapan"], "Penetapan penerima melalui Keputusan Gubernur: 22 sampai 29 Oktober 2026",
     "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"),
    (["kjmu", "jadwal"], "Penetapan penerima melalui Keputusan Gubernur: 22 sampai 29 Oktober 2026",
     "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"),
    (["kjmu", "pengumuman"], "Penetapan penerima melalui Keputusan Gubernur: 22 sampai 29 Oktober 2026",
     "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"),
    (["kjmu", "penetapan"], "Penetapan penerima melalui Keputusan Gubernur: 22 sampai 29 Oktober 2026",
     "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"),
    (["kjmu", "cair"], "Penetapan penerima melalui Keputusan Gubernur: 22 sampai 29 Oktober 2026",
     "infografis_kjmu_tahap_ii_2026_diperpanjang.txt"),
]


def ubah_jadi_kata(teks):
    """Huruf kecil, buang tanda baca, pisah per kata, buang kata umum."""
    teks = teks.lower()
    teks = re.sub(r"[^a-z0-9]+", " ", teks)
    hasil = []
    for kata in teks.split():
        if kata in KATA_UMUM:
            continue
        if len(kata) < 2:
            continue
        hasil.append(kata)
    return hasil


def tambah_kata_sepadan(daftar_kata):
    hasil = list(daftar_kata)
    for kata in daftar_kata:
        if kata in KATA_SEPADAN:
            for tambahan in KATA_SEPADAN[kata]:
                if tambahan not in hasil:
                    hasil.append(tambahan)
    return hasil


class Indeks:
    """Indeks pencarian. Dibangun sekali saat aplikasi pertama kali bertanya."""

    def __init__(self):
        self.dokumen, self.potongan = muat_semua_potongan()

        # Untuk setiap potongan: jumlah kemunculan tiap kata, dan panjang potongan (dalam kata).
        # Judul dokumen ikut dihitung supaya pertanyaan "syarat KJMU" cocok ke dokumen KJMU.
        self.hitungan_kata = []
        self.panjang = []
        for potongan in self.potongan:
            dokumen = self.dokumen[potongan["nomor_dokumen"]]
            kata = ubah_jadi_kata(dokumen["judul"] + " " + potongan["teks"])
            hitungan = {}
            for k in kata:
                hitungan[k] = hitungan.get(k, 0) + 1
            self.hitungan_kata.append(hitungan)
            self.panjang.append(len(kata))

        jumlah_potongan = len(self.potongan)
        if jumlah_potongan > 0:
            self.panjang_rata = sum(self.panjang) / jumlah_potongan
        else:
            self.panjang_rata = 1

        # Berapa potongan yang memuat setiap kata (untuk menilai kata jarang vs kata umum)
        self.jumlah_potongan_berisi = {}
        for hitungan in self.hitungan_kata:
            for k in hitungan:
                self.jumlah_potongan_berisi[k] = self.jumlah_potongan_berisi.get(k, 0) + 1

    def nilai_kata(self, kata):
        """Bobot kata: makin jarang muncul di dokumen, makin tinggi."""
        n = len(self.potongan)
        berisi = self.jumlah_potongan_berisi.get(kata, 0)
        return math.log(1 + (n - berisi + 0.5) / (berisi + 0.5))

    def cari(self, pertanyaan, jumlah=4):
        """Mengembalikan daftar (skor, potongan) urut dari yang paling cocok."""
        kata_asli = ubah_jadi_kata(pertanyaan)
        kata_cari = tambah_kata_sepadan(kata_asli)
        if len(kata_cari) == 0:
            return []

        hasil = []
        for nomor in range(len(self.potongan)):
            hitungan = self.hitungan_kata[nomor]
            skor = 0.0
            for kata in kata_cari:
                frekuensi = hitungan.get(kata, 0)
                if frekuensi == 0:
                    continue
                pembilang = frekuensi * (K1 + 1)
                penyebut = frekuensi + K1 * (1 - B + B * self.panjang[nomor] / self.panjang_rata)
                bobot = self.nilai_kata(kata)
                # Kata yang benar-benar ditulis warga lebih penting daripada kata sepadan
                if kata not in kata_asli:
                    bobot = bobot * 0.5
                skor = skor + bobot * pembilang / penyebut
            if skor > 0:
                hasil.append((skor, self.potongan[nomor]))

        hasil.sort(key=lambda pasangan: pasangan[0], reverse=True)
        hasil = hasil[:jumlah]

        # Sisipkan potongan penting di urutan kedua kalau belum terbawa
        for kata_wajib, penggalan, nama_file in POTONGAN_PENTING:
            semua_ada = True
            for kata in kata_wajib:
                if kata not in kata_asli:
                    semua_ada = False
                    break
            if not semua_ada:
                continue
            potongan_penting = self.cari_potongan_berisi(penggalan, nama_file)
            if potongan_penting is None:
                continue
            sudah_ada = False
            for skor, potongan in hasil:
                if potongan["id"] == potongan_penting["id"]:
                    sudah_ada = True
            if not sudah_ada:
                hasil.insert(1, (0.0, potongan_penting))
                hasil = hasil[:jumlah]

        return hasil

    def cari_potongan_berisi(self, penggalan, nama_file):
        """Potongan dari file tertentu yang memuat penggalan teks. None kalau tidak ada."""
        penggalan = " ".join(penggalan.split())
        for potongan in self.potongan:
            dokumen = self.dokumen[potongan["nomor_dokumen"]]
            if dokumen["nama_file"] != nama_file:
                continue
            if penggalan in " ".join(potongan["teks"].split()):
                return potongan
        return None


_indeks = None


def ambil_indeks():
    """Indeks dibuat sekali saja, lalu dipakai ulang."""
    global _indeks
    if _indeks is None:
        _indeks = Indeks()
    return _indeks
