"""
Membuat tautan dan gambar QR untuk menghubungkan pengajuan ke bot Telegram.

Isi QR: https://t.me/<nama_bot>?start=<kode_pengajuan>
Saat dipindai lalu warga menekan Start, bot menerima pesan "/start JHJ0051",
dan W0 menempelkan chat_id warga ke pengajuan itu (kontrak data bagian 6).
"""

import io

import qrcode

from pengaturan import TELEGRAM_BOT_USERNAME, ambil_pengaturan


def nama_bot():
    """Nama bot dari .env, tanpa tanda @ di depan. Kosong kalau belum diisi."""
    nama = ambil_pengaturan(TELEGRAM_BOT_USERNAME)
    if nama.startswith("@"):
        nama = nama[1:]
    return nama


def tautan_telegram(kode_pengajuan):
    """Tautan t.me untuk kode pengajuan, atau teks kosong kalau nama bot belum diisi."""
    nama = nama_bot()
    if nama == "":
        return ""
    return "https://t.me/" + nama + "?start=" + kode_pengajuan


def gambar_qr(teks):
    """Gambar QR (PNG) dalam bentuk bytes, siap ditampilkan dengan st.image."""
    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(teks)
    qr.make(fit=True)
    gambar = qr.make_image(fill_color="black", back_color="white")
    wadah = io.BytesIO()
    gambar.save(wadah, format="PNG")
    return wadah.getvalue()
