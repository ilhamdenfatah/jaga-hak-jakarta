-- =====================================================================
-- Jaga Hak Jakarta: skema database Supabase
-- Versi 1, 14 Oktober 2026
--
-- Cara pakai:
--   1. Buka proyek Supabase, menu SQL Editor, buat query baru.
--   2. Tempel seluruh isi file ini, klik Run. Cukup sekali.
--   3. Cek menu Table Editor: harus ada 5 tabel dan 1 view.
--
-- Penjelasan setiap kolom ada di docs/kontrak_data.md.
-- Semua data di database ini FIKTIF. Jangan pernah mengisi NIK, KK,
-- nomor HP, atau alamat lengkap orang sungguhan.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. Tabel aturan_program
--    Diisi Jalur A (PJ A). Dibaca halaman Warga untuk pemeriksaan program.
-- ---------------------------------------------------------------------
create table aturan_program (
    kode_program            text primary key,
    nama_program            text not null,
    kelompok_sasaran        text not null
        check (kelompok_sasaran in ('siswa', 'mahasiswa', 'lansia',
                                    'disabilitas', 'anak_usia_dini', 'keluarga')),
    jenjang_berlaku         text,      -- contoh: 'SD,SMP,SMA,SMK' atau 'PT'. Kosong = tidak dibatasi jenjang
    usia_min                integer,
    usia_max                integer,
    min_lama_domisili_tahun integer,
    desil_maks              integer check (desil_maks between 1 and 10),
    tanggal_buka            date,
    tanggal_tutup           date,
    keterangan_jadwal       text,      -- dipakai kalau jadwal tidak berupa tanggal pasti
    langkah_pengajuan       text,
    berkas_wajib            text,      -- dipisah titik koma, contoh: 'Kartu Keluarga; Akta kelahiran'
    sumber_judul            text not null,
    sumber_tautan           text,
    sumber_tanggal_akses    date,
    adalah_contoh           boolean not null default false,
    aktif                   boolean not null default true,
    diperbarui_pada         timestamptz not null default now()
);


-- ---------------------------------------------------------------------
-- 2. Tabel rumah_tangga
--    Data simulasi 300 rumah tangga dari Jalur B, termasuk persona demo.
-- ---------------------------------------------------------------------
create table rumah_tangga (
    id                              bigint generated always as identity primary key,
    nama_perwakilan                 text not null,   -- fiktif, contoh 'Bu Lia'
    kelurahan                       text not null,
    kecamatan                       text not null,
    rw                              text,
    rt                              text,
    jumlah_anggota                  integer check (jumlah_anggota > 0),
    jenjang_anak                    text,            -- jenjang anak utama, boleh kosong
    usia_anak                       integer,
    ada_lansia                      boolean not null default false,
    ada_disabilitas                 boolean not null default false,
    lama_domisili_tahun             integer,
    desil_menurut_warga             integer check (desil_menurut_warga between 1 and 10),
    desil_sebelumnya_menurut_warga  integer check (desil_sebelumnya_menurut_warga between 1 and 10),
    adalah_persona                  boolean not null default false,
    catatan                         text,
    dibuat_pada                     timestamptz not null default now()
);


-- ---------------------------------------------------------------------
-- 3. Tabel pengajuan
--    Ditulis W1 (pengajuan baru), W0 (chat_id Telegram), W2 (status),
--    W3 (penanda pengingat dan eskalasi). Dibaca halaman Kelurahan dan W4.
-- ---------------------------------------------------------------------

-- Penghitung nomor urut untuk kode pengajuan: JHJ0001, JHJ0002, dan seterusnya
create sequence nomor_pengajuan_seq;

-- Fungsi pembuat kode pengajuan. Minimal 4 digit, tidak terpotong kalau lewat 9999.
create function buat_kode_pengajuan() returns text
language plpgsql
as $$
declare
    nomor text;
begin
    nomor := nextval('nomor_pengajuan_seq')::text;
    if length(nomor) < 4 then
        nomor := lpad(nomor, 4, '0');
    end if;
    return 'JHJ' || nomor;
end;
$$;

create table pengajuan (
    id                              bigint generated always as identity primary key,
    kode_pengajuan                  text not null unique default buat_kode_pengajuan(),
    sumber_data                     text not null default 'stan'
        check (sumber_data in ('simulasi', 'stan', 'uji')),
    id_rumah_tangga                 bigint references rumah_tangga(id) on delete set null,

    -- Data dari formulir halaman Warga
    nama_pemohon                    text not null,   -- fiktif atau nama samaran
    kelurahan                       text not null,
    kecamatan                       text,
    kode_program                    text not null references aturan_program(kode_program),
    jenjang_anak                    text,
    usia_sasaran                    integer,         -- usia orang yang dibantu (anak, lansia, dan sebagainya)
    ada_lansia                      boolean not null default false,
    ada_disabilitas                 boolean not null default false,
    desil_menurut_warga             integer check (desil_menurut_warga between 1 and 10),
    desil_sebelumnya_menurut_warga  integer check (desil_sebelumnya_menurut_warga between 1 and 10),
    tenggat_program                 date,            -- disalin dari aturan_program.tanggal_tutup saat diajukan
    kronologi                       text not null,

    -- Diisi otomatis
    ringkasan_ai                    text,            -- ringkasan kronologi oleh Gemini (W1), hanya untuk dibaca petugas
    status                          text not null default 'Diterima'
        check (status in ('Diterima', 'Sedang diverifikasi',
                          'Perlu berkas tambahan', 'Diteruskan ke dinas')),
    catatan_petugas                 text,
    nama_petugas                    text,

    -- Telegram (diisi W0 setelah warga memindai QR dan menekan Start)
    telegram_chat_id                bigint,
    telegram_terhubung_pada         timestamptz,

    -- Batas waktu tindak lanjut petugas (dipakai W3).
    -- Default di bawah adalah MODE DEMO: pengingat 3 menit, eskalasi 5 menit.
    waktu_pengingat                 timestamptz not null default now() + interval '3 minutes',
    batas_tindak_lanjut             timestamptz not null default now() + interval '5 minutes',
    pengingat_terkirim_pada         timestamptz,
    eskalasi_terkirim_pada          timestamptz,

    dibuat_pada                     timestamptz not null default now(),
    diperbarui_pada                 timestamptz not null default now()
);

-- Isi otomatis kolom diperbarui_pada setiap kali baris pengajuan diubah
create function isi_waktu_diperbarui() returns trigger
language plpgsql
as $$
begin
    new.diperbarui_pada := now();
    return new;
end;
$$;

create trigger pengajuan_diperbarui
    before update on pengajuan
    for each row execute function isi_waktu_diperbarui();


-- ---------------------------------------------------------------------
-- 4. Tabel log_notifikasi
--    Setiap pesan Telegram yang dikirim workflow dicatat di sini.
-- ---------------------------------------------------------------------
create table log_notifikasi (
    id                  bigint generated always as identity primary key,
    kode_pengajuan      text references pengajuan(kode_pengajuan) on delete cascade,
    workflow            text not null check (workflow in ('W0', 'W1', 'W2', 'W3', 'W4', 'W5')),
    jenis               text not null
        check (jenis in ('tiket', 'alert_prioritas', 'status', 'pengingat',
                         'eskalasi', 'laporan_harian', 'komunitas', 'balasan_otomatis')),
    penerima            text not null
        check (penerima in ('warga', 'petugas', 'atasan', 'pimpinan', 'rt_rw')),
    telegram_chat_id    bigint,
    isi_pesan           text,
    berhasil            boolean not null default true,
    pesan_error         text,
    dikirim_pada        timestamptz not null default now()
);


-- ---------------------------------------------------------------------
-- 5. Tabel kontak_internal
--    Daftar penerima pesan di sisi pemerintah (semua diperankan anggota tim).
--    Ganti chat_id di sini saja, tidak perlu mengubah workflow.
-- ---------------------------------------------------------------------
create table kontak_internal (
    id                  bigint generated always as identity primary key,
    peran               text not null check (peran in ('petugas', 'atasan', 'pimpinan', 'rt_rw')),
    nama                text not null,     -- label peran, contoh 'Petugas Kelurahan (contoh)'
    telegram_chat_id    bigint not null,
    kelurahan           text,
    aktif               boolean not null default true
);


-- ---------------------------------------------------------------------
-- 6. Rumus skor prioritas
--    Satu rumus untuk semua: halaman Kelurahan, W1, W4, dan data simulasi.
--    Tidak memakai AI. Input yang sama selalu menghasilkan skor yang sama.
-- ---------------------------------------------------------------------
create function hitung_skor_prioritas(
    tenggat date,
    ada_lansia boolean,
    ada_disabilitas boolean
) returns integer
language plpgsql
stable
as $$
declare
    hari_ini  date;
    sisa_hari integer;
    skor      integer := 0;
begin
    -- Tanggal hari ini menurut jam Jakarta, bukan jam server (UTC)
    hari_ini := (now() at time zone 'Asia/Jakarta')::date;

    -- Bagian 1: tenggat program
    if tenggat is not null then
        sisa_hari := tenggat - hari_ini;
        if sisa_hari < 0 then
            skor := skor + 0;     -- tenggat sudah lewat, ditandai terpisah
        elsif sisa_hari <= 3 then
            skor := skor + 50;
        elsif sisa_hari <= 7 then
            skor := skor + 30;
        elsif sisa_hari <= 14 then
            skor := skor + 15;
        end if;
    end if;

    -- Bagian 2: kelompok rentan di rumah
    if ada_lansia then
        skor := skor + 15;
    end if;
    if ada_disabilitas then
        skor := skor + 15;
    end if;

    return skor;
end;
$$;


-- ---------------------------------------------------------------------
-- 7. View antrean_kelurahan
--    Dibaca halaman Kelurahan dan W1. Skor dihitung ulang setiap kali
--    dibaca, jadi ikut naik saat tenggat makin dekat.
-- ---------------------------------------------------------------------
create view antrean_kelurahan as
select
    p.kode_pengajuan,
    p.sumber_data,
    p.nama_pemohon,
    p.kelurahan,
    p.kode_program,
    a.nama_program,
    p.status,
    p.tenggat_program,
    p.tenggat_program - (now() at time zone 'Asia/Jakarta')::date as sisa_hari_tenggat,
    case
        when p.tenggat_program is null then null
        when p.tenggat_program < (now() at time zone 'Asia/Jakarta')::date then 'Lewat tenggat'
        when p.tenggat_program - (now() at time zone 'Asia/Jakarta')::date <= 7 then 'Tenggat dekat'
        else null
    end as tanda_tenggat,
    (p.ada_lansia or p.ada_disabilitas) as kelompok_rentan,
    hitung_skor_prioritas(p.tenggat_program, p.ada_lansia, p.ada_disabilitas) as skor_prioritas,
    case
        when hitung_skor_prioritas(p.tenggat_program, p.ada_lansia, p.ada_disabilitas) >= 50 then 'Tinggi'
        when hitung_skor_prioritas(p.tenggat_program, p.ada_lansia, p.ada_disabilitas) >= 20 then 'Sedang'
        else 'Rendah'
    end as kategori_prioritas,
    p.ringkasan_ai,
    p.kronologi,
    p.catatan_petugas,
    (p.telegram_chat_id is not null) as telegram_terhubung,
    (p.status = 'Diterima' and now() > p.batas_tindak_lanjut) as lewat_batas_tindak_lanjut,
    p.dibuat_pada,
    p.diperbarui_pada
from pengajuan p
join aturan_program a on a.kode_program = p.kode_program;


-- ---------------------------------------------------------------------
-- 8. Keamanan: aktifkan Row Level Security di semua tabel
--    Tabel yang dibuat lewat SQL Editor TIDAK otomatis aktif RLS-nya.
--    Kita sengaja tidak membuat policy apa pun: artinya kunci publik
--    (publishable/anon) tidak bisa membaca apa-apa. Streamlit dan n8n
--    tetap bisa, karena memakai connection string database atau secret key.
-- ---------------------------------------------------------------------
alter table aturan_program  enable row level security;
alter table rumah_tangga    enable row level security;
alter table pengajuan       enable row level security;
alter table log_notifikasi  enable row level security;
alter table kontak_internal enable row level security;

-- View mengikuti hak akses pembacanya, supaya tidak jadi pintu belakang lewat API
alter view antrean_kelurahan set (security_invoker = true);


-- ---------------------------------------------------------------------
-- 9. Data aturan program CONTOH
--    Hanya untuk uji coba sampai tabel asli dari PJ A masuk.
--    Angka syarat dan tanggal di bawah BUKAN aturan resmi.
--    Setelah tabel PJ A siap, hapus dengan:
--      delete from aturan_program where adalah_contoh = true;
--    (Gagal kalau sudah ada pengajuan yang memakai kodenya. Hapus dulu
--     pengajuan uji, atau timpa barisnya dengan data asli.)
-- ---------------------------------------------------------------------
insert into aturan_program
    (kode_program, nama_program, kelompok_sasaran, jenjang_berlaku, usia_min, usia_max,
     min_lama_domisili_tahun, desil_maks, tanggal_buka, tanggal_tutup, keterangan_jadwal,
     langkah_pengajuan, berkas_wajib, sumber_judul, adalah_contoh)
values
    ('KJP_PLUS', 'KJP Plus', 'siswa', 'SD,SMP,SMA,SMK', 6, 21,
     null, 5, '2026-10-19', '2026-10-30', null,
     'CONTOH: langkah diisi PJ A dari pengumuman resmi Disdik.',
     'CONTOH: Kartu Keluarga; Kartu pelajar; Tangkapan layar hasil Cek Bansos',
     'CONTOH: belum diisi PJ A', true),

    ('KJMU', 'KJMU', 'mahasiswa', 'PT', null, null,
     null, null, null, '2026-10-06', null,
     'CONTOH: langkah diisi PJ A dari pengumuman resmi Disdik.',
     'CONTOH: Kartu Keluarga; Kartu tanda mahasiswa',
     'CONTOH: belum diisi PJ A', true),

    ('KLJ', 'Kartu Lansia Jakarta', 'lansia', null, null, null,
     null, null, null, null, 'CONTOH: jadwal mengikuti pengumuman resmi',
     'CONTOH: langkah diisi PJ A.', 'CONTOH: Kartu Keluarga',
     'CONTOH: belum diisi PJ A', true),

    ('KPDJ', 'Kartu Penyandang Disabilitas Jakarta', 'disabilitas', null, null, null,
     null, null, null, null, 'CONTOH: jadwal mengikuti pengumuman resmi',
     'CONTOH: langkah diisi PJ A.', 'CONTOH: Kartu Keluarga',
     'CONTOH: belum diisi PJ A', true),

    ('KAJ', 'Kartu Anak Jakarta', 'anak_usia_dini', null, null, null,
     null, null, null, null, 'CONTOH: jadwal mengikuti pengumuman resmi',
     'CONTOH: langkah diisi PJ A.', 'CONTOH: Kartu Keluarga; Akta kelahiran',
     'CONTOH: belum diisi PJ A', true),

    ('USUL_SANGGAH', 'Usul sanggah data melalui aplikasi Cek Bansos', 'keluarga', null, null, null,
     null, null, null, null, 'CONTOH: dapat diajukan kapan saja melalui jalur resmi',
     'CONTOH: langkah diisi PJ A dari panduan resmi Kemensos.', 'CONTOH: diisi PJ A',
     'CONTOH: belum diisi PJ A', true);
