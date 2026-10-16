"""
Halaman Warga: loket depan (PC 1).

Isi halaman:
- Pilihan tokoh (persona) supaya pengunjung tidak perlu mengetik banyak.
- Tab 1 Tanya jawab      : chatbot dari Jalur A (disambungkan di tahap berikutnya).
- Tab 2 Periksa program  : formulir singkat, lalu daftar program yang dapat diajukan.
                           Hasilnya dari tabel aturan_program, tanpa AI.
- Tab 3 Siapkan pengajuan: kronologi, unduh surat (Word), tombol Ajukan, lalu kode dan QR Telegram.

Halaman ini hanya MEMBACA dari database. Pengajuan dikirim lewat n8n (W1).
"""

import pandas as pd
import streamlit as st

import db
import pemeriksa_program as pp
import penyusun_surat
import qr_telegram
import webhook
from pengaturan import TEKS_SIMULASI, ambil_sumber_data


st.set_page_config(page_title="Jaga Hak Jakarta", layout="centered")

# Menghilangkan garis biru penanda fokus yang muncul di tab setelah diklik pakai mouse
st.markdown(
    """
    <style>
    [role="tab"]:focus:not(:focus-visible),
    [role="tabpanel"]:focus,
    [role="tabpanel"]:focus-visible { outline: none; box-shadow: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

PANJANG_MINIMAL_KRONOLOGI = 20


KECAMATAN_JAKARTA_BARAT = [
    "Cengkareng",
    "Grogol Petamburan",
    "Kalideres",
    "Kebon Jeruk",
    "Kembangan",
    "Palmerah",
    "Taman Sari",
    "Tambora",
]

DESIL_BELUM_TAHU = "Belum tahu"
PILIHAN_DESIL = [DESIL_BELUM_TAHU, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

TAB_TANYA = "1. Tanya jawab"
TAB_PERIKSA = "2. Periksa program"
TAB_AJUKAN = "3. Siapkan pengajuan"

PILIHAN_ISI_SENDIRI = "Isi sendiri"

WARNA_HASIL = {
    pp.HASIL_DAPAT: "green",
    pp.HASIL_TERKENDALA: "orange",
    pp.HASIL_BELUM_SESUAI: "gray",
}


# ---------------------------------------------------------------------
# Bantuan kecil
# ---------------------------------------------------------------------

def jadi_angka(nilai):
    """Angka dari database (bisa 14.0 atau NaN) menjadi int, atau None kalau kosong."""
    if pp.kosong(nilai):
        return None
    return int(nilai)


def jadi_ya_tidak(nilai):
    """Nilai ya/tidak dari database menjadi True atau False. Kosong dianggap False."""
    if pp.kosong(nilai):
        return False
    return bool(nilai)


def label_jenjang_dari_kode(kode):
    """'SMP' menjadi 'SMP', 'PT' menjadi 'Perguruan tinggi', kosong menjadi pilihan pertama."""
    for label, kode_jenjang in pp.PILIHAN_JENJANG.items():
        if kode_jenjang == kode:
            return label
    return list(pp.PILIHAN_JENJANG.keys())[0]


def desil_ke_pilihan(nilai):
    """Desil dari database (angka atau kosong) menjadi pilihan di formulir."""
    angka = jadi_angka(nilai)
    if angka is None:
        return DESIL_BELUM_TAHU
    return angka


def pilihan_ke_desil(pilihan):
    """Pilihan di formulir menjadi angka, atau None kalau 'Belum tahu'."""
    if pilihan == DESIL_BELUM_TAHU:
        return None
    return int(pilihan)


# ---------------------------------------------------------------------
# Aksi tombol (dijalankan Streamlit sebelum halaman digambar ulang)
# ---------------------------------------------------------------------

def isi_dari_persona():
    """Mengisi formulir dari tokoh yang dipilih, atau mengosongkannya kalau 'Isi sendiri'."""
    pilihan = st.session_state["pilihan_persona"]
    daftar_persona = st.session_state["daftar_persona"]

    # Setiap ganti tokoh, hasil pemeriksaan lama dibuang supaya tidak tertukar
    st.session_state.pop("hasil_periksa", None)
    st.session_state.pop("isian", None)
    st.session_state.pop("program_terpilih", None)
    st.session_state.pop("hasil_ajukan", None)
    st.session_state.pop("kronologi", None)

    if pilihan == PILIHAN_ISI_SENDIRI:
        st.session_state["id_rumah_tangga"] = None
        st.session_state["nama_pemohon"] = ""
        st.session_state["kelurahan"] = ""
        st.session_state["kecamatan"] = KECAMATAN_JAKARTA_BARAT[0]
        st.session_state["jenjang"] = list(pp.PILIHAN_JENJANG.keys())[0]
        st.session_state["usia_sasaran"] = None
        st.session_state["ada_lansia"] = False
        st.session_state["ada_disabilitas"] = False
        st.session_state["lama_domisili"] = None
        st.session_state["desil_sekarang"] = DESIL_BELUM_TAHU
        st.session_state["desil_sebelumnya"] = DESIL_BELUM_TAHU
        return

    persona = daftar_persona[daftar_persona["nama_perwakilan"] == pilihan].iloc[0]
    st.session_state["id_rumah_tangga"] = int(persona["id"])
    st.session_state["nama_pemohon"] = str(persona["nama_perwakilan"])
    st.session_state["kelurahan"] = str(persona["kelurahan"])
    st.session_state["kecamatan"] = str(persona["kecamatan"])
    st.session_state["jenjang"] = label_jenjang_dari_kode(persona["jenjang_anak"])
    st.session_state["usia_sasaran"] = jadi_angka(persona["usia_anak"])
    st.session_state["ada_lansia"] = jadi_ya_tidak(persona["ada_lansia"])
    st.session_state["ada_disabilitas"] = jadi_ya_tidak(persona["ada_disabilitas"])
    st.session_state["lama_domisili"] = jadi_angka(persona["lama_domisili_tahun"])
    st.session_state["desil_sekarang"] = desil_ke_pilihan(persona["desil_menurut_warga"])
    st.session_state["desil_sebelumnya"] = desil_ke_pilihan(persona["desil_sebelumnya_menurut_warga"])


def mulai_ulang():
    """Mengosongkan semua isian untuk pengunjung berikutnya."""
    for kunci in list(st.session_state.keys()):
        del st.session_state[kunci]


def pilih_program(hasil_program):
    """Menyimpan program yang dipilih, lalu pindah ke tab Siapkan pengajuan."""
    st.session_state["program_terpilih"] = hasil_program
    st.session_state["tab_aktif"] = TAB_AJUKAN
    st.session_state.pop("hasil_ajukan", None)

    # Untuk tokoh contoh, kronologi diisi otomatis supaya demo tidak menunggu pengunjung mengetik.
    # Untuk "Isi sendiri", kronologi dibiarkan kosong supaya ditulis pengunjung sendiri.
    isian = st.session_state["isian"]
    if isian["id_rumah_tangga"] is not None:
        st.session_state["kronologi"] = penyusun_surat.kronologi_contoh(isian, hasil_program)
    elif "kronologi" not in st.session_state:
        st.session_state["kronologi"] = ""


def susun_data_w1(isian, program, kronologi):
    """Paket data untuk W1. Nama kunci persis seperti kontrak data bagian 9."""
    tenggat = None
    if program["tanggal_tutup"] is not None:
        tenggat = program["tanggal_tutup"].strftime("%Y-%m-%d")

    return {
        "sumber_data": ambil_sumber_data(),
        "id_rumah_tangga": isian["id_rumah_tangga"],
        "nama_pemohon": isian["nama_pemohon"],
        "kelurahan": isian["kelurahan"],
        "kecamatan": isian["kecamatan"],
        "kode_program": program["kode_program"],
        "jenjang_anak": isian["jenjang_anak"],
        "usia_sasaran": isian["usia_sasaran"],
        "ada_lansia": bool(isian["ada_lansia"]),
        "ada_disabilitas": bool(isian["ada_disabilitas"]),
        "desil_menurut_warga": isian["desil_menurut_warga"],
        "desil_sebelumnya_menurut_warga": isian["desil_sebelumnya_menurut_warga"],
        "tenggat_program": tenggat,
        "kronologi": kronologi.strip(),
    }


# ---------------------------------------------------------------------
# Tampilan satu kartu program
# ---------------------------------------------------------------------

def tampilkan_kartu_program(hasil, nomor):
    with st.container(border=True):
        st.markdown("**" + hasil["nama_program"] + "**")
        st.badge(hasil["hasil"], color=WARNA_HASIL[hasil["hasil"]])
        st.write(hasil["jadwal"])

        if hasil["adalah_contoh"]:
            st.caption("Data contoh untuk uji coba, bukan aturan resmi.")

        if hasil["hasil"] == pp.HASIL_TERKENDALA:
            for alasan in hasil["alasan"]:
                st.write(alasan)
            st.write(
                "Anda tetap dapat mengajukan ke kelurahan untuk didampingi. Bila menurut Anda "
                "data keluarga di Cek Bansos tidak sesuai dengan kondisi sebenarnya, jalur resminya "
                "adalah usul sanggah melalui aplikasi Cek Bansos. Lampirkan tangkapan layar hasil "
                "Cek Bansos saat mengajukan."
            )
        elif hasil["hasil"] == pp.HASIL_BELUM_SESUAI:
            for alasan in hasil["alasan"]:
                st.write(alasan)

        for catatan in hasil["catatan"]:
            st.caption(catatan)

        with st.expander("Langkah, berkas, dan sumber"):
            if len(hasil["berkas"]) > 0:
                st.markdown("Berkas yang perlu disiapkan:")
                for berkas in hasil["berkas"]:
                    st.markdown("- " + berkas)
            if not pp.kosong(hasil["langkah"]):
                st.markdown("Langkah pengajuan:")
                st.write(hasil["langkah"])

            teks_sumber = "Sumber: " + str(hasil["sumber_judul"])
            if not pp.kosong(hasil["sumber_tanggal_akses"]):
                teks_sumber = teks_sumber + ", diakses " + pp.format_tanggal(hasil["sumber_tanggal_akses"])
            st.caption(teks_sumber)
            if not pp.kosong(hasil["sumber_tautan"]):
                st.caption(str(hasil["sumber_tautan"]))

        if hasil["hasil"] != pp.HASIL_BELUM_SESUAI:
            st.button(
                "Siapkan pengajuan " + hasil["nama_program"],
                key="pilih_" + hasil["kode_program"] + "_" + str(nomor),
                type="primary",
                on_click=pilih_program,
                args=(hasil,),
            )


# ---------------------------------------------------------------------
# Kepala halaman
# ---------------------------------------------------------------------

kolom_judul, kolom_ulang = st.columns([3, 1], vertical_alignment="bottom")
with kolom_judul:
    st.title("Jaga Hak Jakarta")
with kolom_ulang:
    st.button("Mulai ulang", on_click=mulai_ulang, width="stretch",
              help="Kosongkan semua isian untuk pengunjung berikutnya.")

st.write("Memahami hak bantuan, memeriksa program yang dapat diajukan, "
         "dan menyiapkan pengajuan ke kelurahan.")
st.caption(TEKS_SIMULASI)


# ---------------------------------------------------------------------
# Ambil data dari database
# ---------------------------------------------------------------------

try:
    tabel_aturan = db.ambil_aturan_program()
    daftar_persona = db.ambil_persona()
except db.DatabaseGagal as error:
    st.error("Data belum bisa dimuat. " + str(error))
    st.stop()

st.session_state["daftar_persona"] = daftar_persona

# Isi awal formulir, hanya sekali di awal sesi atau setelah Mulai ulang
if "nama_pemohon" not in st.session_state:
    st.session_state["pilihan_persona"] = PILIHAN_ISI_SENDIRI
    isi_dari_persona()


# ---------------------------------------------------------------------
# Pilihan tokoh
# ---------------------------------------------------------------------

pilihan_persona = [PILIHAN_ISI_SENDIRI]
for _, persona in daftar_persona.iterrows():
    pilihan_persona.append(str(persona["nama_perwakilan"]))

st.selectbox(
    "Pakai contoh tokoh, atau isi sendiri",
    pilihan_persona,
    key="pilihan_persona",
    on_change=isi_dari_persona,
    help="Tokoh contoh berisi data fiktif, supaya Anda tidak perlu mengetik banyak.",
)

if len(daftar_persona) == 0:
    st.caption("Contoh tokoh belum tersedia. Silakan isi sendiri.")
else:
    pilihan = st.session_state["pilihan_persona"]
    if pilihan != PILIHAN_ISI_SENDIRI:
        persona = daftar_persona[daftar_persona["nama_perwakilan"] == pilihan].iloc[0]
        if not pp.kosong(persona["catatan"]):
            st.caption("Cerita singkat: " + str(persona["catatan"]))


# ---------------------------------------------------------------------
# Tiga tab
# ---------------------------------------------------------------------

tab_tanya, tab_periksa, tab_ajukan = st.tabs(
    [TAB_TANYA, TAB_PERIKSA, TAB_AJUKAN],
    key="tab_aktif",
    default=TAB_PERIKSA,
    on_change="rerun",  # wajib, supaya tab bisa dipindah otomatis lewat tombol
)


# ----- Tab 1: Tanya jawab --------------------------------------------

with tab_tanya:
    st.info("Tanya jawab sedang disiapkan. Untuk sementara, silakan lanjut ke Periksa program.")


# ----- Tab 2: Periksa program ----------------------------------------

with tab_periksa:
    with st.form("form_pemeriksa"):
        st.markdown("**Data singkat**")
        st.text_input("Nama atau nama samaran", key="nama_pemohon",
                      help="Tidak perlu nama asli. Jangan mengisi NIK, nomor KK, atau nomor HP.")

        # Kalau kecamatan dari tokoh tidak ada di daftar, tambahkan supaya tetap bisa dipilih
        daftar_kecamatan = list(KECAMATAN_JAKARTA_BARAT)
        if st.session_state["kecamatan"] not in daftar_kecamatan:
            daftar_kecamatan.append(st.session_state["kecamatan"])

        kolom_a, kolom_b = st.columns(2)
        with kolom_a:
            st.selectbox("Kecamatan", daftar_kecamatan, key="kecamatan")
        with kolom_b:
            st.text_input("Kelurahan", key="kelurahan")

        st.markdown("**Siapa yang perlu dibantu**")
        kolom_c, kolom_d = st.columns(2)
        with kolom_c:
            st.selectbox("Jenjang sekolah atau kuliah", list(pp.PILIHAN_JENJANG.keys()), key="jenjang")
        with kolom_d:
            st.number_input("Usia orang yang dibantu (tahun)", min_value=0, max_value=120,
                            step=1, key="usia_sasaran", placeholder="Boleh dikosongkan")

        st.checkbox("Ada lansia (60 tahun ke atas) di rumah", key="ada_lansia")
        st.checkbox("Ada penyandang disabilitas di rumah", key="ada_disabilitas")
        st.number_input("Lama tinggal di Jakarta (tahun)", min_value=0, max_value=100,
                        step=1, key="lama_domisili", placeholder="Boleh dikosongkan")

        st.markdown("**Desil keluarga menurut aplikasi Cek Bansos**")
        st.caption("Isi dengan angka yang Anda lihat sendiri. Sistem ini tidak menghitung atau mengubah desil.")
        kolom_e, kolom_f = st.columns(2)
        with kolom_e:
            st.selectbox("Desil sekarang", PILIHAN_DESIL, key="desil_sekarang")
        with kolom_f:
            st.selectbox("Desil sebelumnya", PILIHAN_DESIL, key="desil_sebelumnya")

        tombol_periksa = st.form_submit_button("Periksa", type="primary", width="stretch")

    if tombol_periksa:
        isian = {
            "id_rumah_tangga": st.session_state["id_rumah_tangga"],
            "nama_pemohon": st.session_state["nama_pemohon"].strip(),
            "kelurahan": st.session_state["kelurahan"].strip(),
            "kecamatan": st.session_state["kecamatan"],
            "jenjang_anak": pp.PILIHAN_JENJANG[st.session_state["jenjang"]],
            "usia_sasaran": jadi_angka(st.session_state["usia_sasaran"]),
            "ada_lansia": st.session_state["ada_lansia"],
            "ada_disabilitas": st.session_state["ada_disabilitas"],
            "lama_domisili_tahun": jadi_angka(st.session_state["lama_domisili"]),
            "desil_menurut_warga": pilihan_ke_desil(st.session_state["desil_sekarang"]),
            "desil_sebelumnya_menurut_warga": pilihan_ke_desil(st.session_state["desil_sebelumnya"]),
        }
        st.session_state["isian"] = isian
        st.session_state["hasil_periksa"] = pp.periksa_semua_program(tabel_aturan, isian)
        st.session_state.pop("program_terpilih", None)
        st.session_state.pop("hasil_ajukan", None)

    hasil_periksa = st.session_state.get("hasil_periksa")
    if hasil_periksa is not None:
        isian = st.session_state["isian"]
        st.subheader("Hasil pemeriksaan")

        if pp.desil_naik(isian):
            st.info(
                "Desil yang Anda lihat naik dari " + str(isian["desil_sebelumnya_menurut_warga"])
                + " menjadi " + str(isian["desil_menurut_warga"]) + ". Perubahan desil ditetapkan "
                "pemerintah pusat berdasarkan data DTSEN. Pertanyaan tentang penyebabnya bisa diajukan "
                "di tab Tanya jawab."
            )

        if len(hasil_periksa["program"]) == 0:
            st.write("Dari isian ini, belum ada program bantuan yang cocok. Coba periksa kembali isian "
                     "jenjang, lansia, atau disabilitas, atau tanyakan ke petugas stan.")

        nomor = 0
        for hasil in hasil_periksa["program"]:
            nomor = nomor + 1
            tampilkan_kartu_program(hasil, nomor)

        if len(hasil_periksa["jalur_perbaikan"]) > 0:
            st.subheader("Jalur perbaikan data")
            st.write("Bila data keluarga di Cek Bansos dirasa tidak sesuai dengan kondisi sebenarnya, "
                     "warga dapat mengajukan perbaikan melalui jalur resmi berikut.")
            for hasil in hasil_periksa["jalur_perbaikan"]:
                nomor = nomor + 1
                tampilkan_kartu_program(hasil, nomor)

        st.caption(
            "Hasil ini disusun dari tabel aturan tertulis, bukan tebakan AI. \"Dapat diajukan\" "
            "bukan jaminan diterima. Keputusan penerima bantuan ada di instansi berwenang."
        )


# ----- Tab 3: Siapkan pengajuan --------------------------------------

def tampilkan_hasil_ajukan(hasil_ajukan):
    """Kode pengajuan besar, QR Telegram, dan petunjuk untuk pengunjung."""
    kode = hasil_ajukan["kode_pengajuan"]
    st.success("Pengajuan terkirim ke kelurahan.")

    kolom_kode, kolom_qr = st.columns([3, 2], vertical_alignment="center")
    with kolom_kode:
        st.caption("Nomor tiket Anda")
        st.markdown("## " + kode)
        st.write("Simpan nomor ini. Petugas kelurahan akan menyebut nomor yang sama.")
        tautan = qr_telegram.tautan_telegram(kode)
        if tautan == "":
            st.warning("Nama bot Telegram belum diisi di .env (TELEGRAM_BOT_USERNAME), "
                       "jadi QR belum bisa dibuat. Hubungi petugas stan.")
        else:
            st.markdown("**Supaya mendapat kabar status lewat Telegram:**")
            st.markdown("1. Pindai QR di samping dengan kamera HP.\n"
                        "2. Buka di Telegram, lalu tekan **Start**.\n"
                        "3. Pesan berisi nomor tiket akan masuk dalam beberapa detik.")
            st.caption(tautan)
    with kolom_qr:
        if tautan != "":
            st.image(qr_telegram.gambar_qr(tautan), width=220)

    st.caption("Ingin mencoba lagi atau ganti pengunjung? Tekan Mulai ulang di bagian atas halaman.")


with tab_ajukan:
    program_terpilih = st.session_state.get("program_terpilih")
    if program_terpilih is None:
        st.info("Pilih program dulu di tab Periksa program, lalu klik tombol Siapkan pengajuan.")
    else:
        isian = st.session_state["isian"]

        # Ringkasan program yang dipilih
        st.markdown("**Program:** " + program_terpilih["nama_program"])
        st.badge(program_terpilih["hasil"], color=WARNA_HASIL[program_terpilih["hasil"]])
        st.write("Pemohon: " + (isian["nama_pemohon"] or "(belum diisi)")
                 + ", Kelurahan " + (isian["kelurahan"] or "(belum diisi)"))
        st.write(program_terpilih["jadwal"])

        hasil_ajukan = st.session_state.get("hasil_ajukan")

        if hasil_ajukan is not None and hasil_ajukan.get("ok") is True:
            # Sudah terkirim: tombol Ajukan tidak ditampilkan lagi supaya tidak terkirim dua kali
            tampilkan_hasil_ajukan(hasil_ajukan)
        else:
            # Langkah A: kronologi
            st.markdown("**Ceritakan kronologinya dengan kata-kata Anda sendiri**")
            st.text_area(
                "Kronologi",
                key="kronologi",
                height=150,
                label_visibility="collapsed",
                placeholder="Contoh: Bulan lalu saya cek di aplikasi Cek Bansos, desil keluarga kami naik "
                            "dari 4 menjadi 6. Anak saya kelas 9 dan saya khawatir KJP Plus-nya berhenti.",
                help="Jangan menulis NIK, nomor KK, nomor HP, atau alamat lengkap.",
            )
            kronologi = st.session_state.get("kronologi", "")

            # Langkah B: draf surat dan unduhan Word
            with st.expander("Lihat draf surat permohonan"):
                st.write("Kepada Yth. Lurah " + (isian["kelurahan"] or "-"))
                st.write("Perihal: Permohonan pendampingan pengajuan " + program_terpilih["nama_program"])
                for teks in penyusun_surat.paragraf_isi_surat(isian, program_terpilih):
                    st.write(teks)
                st.markdown("Berkas yang perlu dibawa ke kelurahan:")
                for berkas in penyusun_surat.daftar_berkas_lengkap(program_terpilih):
                    st.markdown("- " + berkas)

            isi_word = penyusun_surat.buat_docx(isian, program_terpilih, kronologi)
            st.download_button(
                "Unduh surat, daftar berkas, dan kronologi (Word)",
                data=isi_word,
                file_name=penyusun_surat.nama_file(isian, program_terpilih),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                width="stretch",
            )

            # Langkah C: pemeriksaan kelengkapan sebelum Ajukan
            kekurangan = []
            if isian["nama_pemohon"] == "":
                kekurangan.append("Nama atau nama samaran belum diisi (di tab Periksa program).")
            if isian["kelurahan"] == "":
                kekurangan.append("Kelurahan belum diisi (di tab Periksa program).")
            if len(kronologi.strip()) < PANJANG_MINIMAL_KRONOLOGI:
                kekurangan.append("Kronologi masih terlalu singkat.")

            for teks in kekurangan:
                st.caption(teks)

            # Pesan dari percobaan Ajukan sebelumnya yang gagal
            if hasil_ajukan is not None:
                if hasil_ajukan.get("mungkin_tersimpan") is True:
                    st.warning(hasil_ajukan["pesan"] + " Minta petugas mengecek layar Kelurahan dulu.")
                else:
                    st.error(hasil_ajukan["pesan"])

            # Langkah D: Ajukan
            tombol_ajukan = st.button(
                "Ajukan ke kelurahan",
                type="primary",
                width="stretch",
                disabled=len(kekurangan) > 0,
            )

            if tombol_ajukan:
                data_w1 = susun_data_w1(isian, program_terpilih, kronologi)
                with st.spinner("Mengirim pengajuan..."):
                    hasil = webhook.kirim_pengajuan(data_w1)

                if hasil["ok"] and pp.kosong(hasil.get("kode_pengajuan")):
                    hasil = {
                        "ok": False,
                        "pesan": "Pengajuan mungkin sudah tersimpan, tetapi nomor tiket tidak diterima.",
                        "mungkin_tersimpan": True,
                    }
                st.session_state["hasil_ajukan"] = hasil
                st.rerun()

        if ambil_sumber_data() == "uji":
            st.caption("Mode uji: pengajuan dari halaman ini ditandai sebagai percobaan tim.")
