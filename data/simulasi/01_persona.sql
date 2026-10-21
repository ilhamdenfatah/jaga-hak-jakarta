-- Jaga Hak Jakarta: 4 persona demonstrasi (fiktif)
-- Dibuat oleh data/simulasi/buat_data_simulasi.py

insert into rumah_tangga (nama_perwakilan, kelurahan, kecamatan, rw, rt, jumlah_anggota, jenjang_anak, usia_anak, ada_lansia, ada_disabilitas, lama_domisili_tahun, desil_menurut_warga, desil_sebelumnya_menurut_warga, catatan, adalah_persona)
select 'Bu Lia', 'Kedoya Utara', 'Kebon Jeruk', '004', '007', 4, 'SMP', 14, false, false, 12, 6, 4, 'Tokoh utama demonstrasi. Anak kelas 9 SMP. Desil keluarga naik dari 4 menjadi 6 sehingga terancam tidak mendapat KJP Plus.', true
where not exists (select 1 from rumah_tangga where adalah_persona = true and nama_perwakilan = 'Bu Lia');

insert into rumah_tangga (nama_perwakilan, kelurahan, kecamatan, rw, rt, jumlah_anggota, jenjang_anak, usia_anak, ada_lansia, ada_disabilitas, lama_domisili_tahun, desil_menurut_warga, desil_sebelumnya_menurut_warga, catatan, adalah_persona)
select 'Bu Siti', 'Cengkareng Timur', 'Cengkareng', '009', '003', 3, 'SMP', 13, false, false, 9, 5, 3, 'Ibu tunggal, buruh cuci dengan penghasilan tidak tetap. Anak kelas VIII SMP sebelumnya menerima KJP Plus. Desil naik dari 3 menjadi 5.', true
where not exists (select 1 from rumah_tangga where adalah_persona = true and nama_perwakilan = 'Bu Siti');

insert into rumah_tangga (nama_perwakilan, kelurahan, kecamatan, rw, rt, jumlah_anggota, jenjang_anak, usia_anak, ada_lansia, ada_disabilitas, lama_domisili_tahun, desil_menurut_warga, desil_sebelumnya_menurut_warga, catatan, adalah_persona)
select 'Bu Dewi', 'Tegal Alur', 'Kalideres', '011', '005', 4, 'SMA', 16, false, false, 15, 7, 7, 'Suami terkena PHK empat bulan lalu dan kini bekerja harian. Data kesejahteraan diduga masih menggambarkan keadaan sebelum PHK. Anak kelas XI SMA.', true
where not exists (select 1 from rumah_tangga where adalah_persona = true and nama_perwakilan = 'Bu Dewi');

insert into rumah_tangga (nama_perwakilan, kelurahan, kecamatan, rw, rt, jumlah_anggota, jenjang_anak, usia_anak, ada_lansia, ada_disabilitas, lama_domisili_tahun, desil_menurut_warga, desil_sebelumnya_menurut_warga, catatan, adalah_persona)
select 'Bu Ratna', 'Meruya Utara', 'Kembangan', '002', '010', 4, 'PT', 18, true, false, 18, 4, 4, 'Ibu dari Aisyah (18), baru lulus SMA dan ingin kuliah. Tinggal bersama adik Aisyah dan nenek. Alamat ayah di dokumen kependudukan berbeda dari tempat tinggal keluarga.', true
where not exists (select 1 from rumah_tangga where adalah_persona = true and nama_perwakilan = 'Bu Ratna');

-- Cek hasil: harus 4 baris
select id, nama_perwakilan, kelurahan, jenjang_anak, desil_sebelumnya_menurut_warga, desil_menurut_warga from rumah_tangga where adalah_persona = true order by id;
