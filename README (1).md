# Sistem Kasir Coffee Shop (Exception Handling)

Repository ini berisi lanjutan proyek UTS mata kuliah Pemrograman Berorientasi Objek dari kelompok kami. Studi kasusnya masih sama, yaitu sistem kasir untuk coffee shop. Bedanya, di tugas ini kami menambahkan exception handling supaya setiap kesalahan input atau pelanggaran aturan bisa dilaporkan dengan jelas ke pemanggilnya, bukan cuma dicetak atau diabaikan begitu saja.

Commit pertama berisi kode UTS yang kami ketik ulang tanpa perubahan. Penambahan exception handling kami lakukan di commit-commit setelahnya, jadi perbedaan sebelum dan sesudahnya bisa dilihat langsung di riwayat git.

## Cara menjalankan

Program ini hanya memakai library bawaan Python (versi 3.8 ke atas), jadi cukup jalankan:

```bash
python kasir_coffee_shop.py
```

---

## 1. Aturan bisnis

Sebelum menulis kode, kami mendata dulu aturan apa saja di coffee shop yang mungkin dilanggar, baik karena salah input maupun karena urutan proses yang keliru. Hasilnya ada 10 aturan. Setiap aturan kami beri kode (AB-01 sampai AB-10) supaya mudah dirujuk di kode dan di pesan error.

| Kode | Aturan bisnis | Dicek di | Exception |
|------|---------------|----------|-----------|
| AB-01 | Harga menu harus berupa angka dan lebih dari 0 | `MenuItem.harga` (setter), `validasi_harga()` | `TypeError`, `ValueError` |
| AB-02 | Ukuran minuman hanya boleh S, M, atau L, dan suhu hanya boleh panas atau dingin | `Minuman.ukuran`, `Minuman.suhu` (setter) | `ValueError` |
| AB-03 | Level pedas minimal 0 dan maksimal 5 | `Makanan.level_pedas` (setter) | `TypeError`, `ValueError` |
| AB-04 | Nama pelanggan tidak boleh kosong | `Pelanggan.nama` (setter) | `TypeError`, `ValueError` |
| AB-05 | Jumlah tiap item pesanan minimal 1 dan maksimal 20 | `ItemPesanan.jumlah` (setter) | `TypeError`, `ValueError` |
| AB-06 | Menu hanya bisa dipesan jika ada di daftar menu dan sedang tersedia | `Pesanan.tambah_item()`, `cari_menu()` | `MenuTidakTersediaError` |
| AB-07 | Pesanan yang sudah dibayar tidak boleh ditambah item atau dibayar lagi | `Pesanan.tambah_item()`, `Pesanan.selesaikan()` | `PesananSudahSelesaiError` |
| AB-08 | Pesanan yang belum berisi item tidak boleh dibayar | `Pesanan.selesaikan()` | `PesananKosongError` |
| AB-09 | Uang yang dibayarkan minimal sebesar total pesanan | `Pesanan.selesaikan()` | `PembayaranKurangError` |
| AB-10 | Poin member tidak boleh ditambah dengan nilai negatif | `PoinMixin.tambah_poin()` | `TypeError`, `ValueError` |

Untuk kesalahan input yang sifatnya umum (tipe data salah atau nilai di luar batas), kami tetap memakai `TypeError` dan `ValueError` bawaan Python. Custom exception kami pakai untuk pelanggaran yang memang khas proses bisnis coffee shop, seperti menu habis atau uang pembayaran kurang.

---

## 2. Hierarki custom exception

Semua exception buatan kami berinduk ke satu base exception, yaitu `CoffeeShopError`. Dengan begitu, kalau ingin menangkap semua error milik aplikasi sekaligus, cukup pakai `except CoffeeShopError`.

```
Exception
└── CoffeeShopError              (base, atribut: kode_aturan)
    ├── MenuTidakTersediaError   (kode_menu, alasan)
    ├── PesananError             (nomor_pesanan)
    │   ├── PesananKosongError
    │   └── PesananSudahSelesaiError   (aksi)
    └── PembayaranKurangError    (total, dibayar, kekurangan)
```

`PesananError` sengaja kami buat sebagai kelompok tersendiri karena `PesananKosongError` dan `PesananSudahSelesaiError` sama-sama berkaitan dengan status pesanan dan sama-sama butuh informasi nomor pesanan.

Setiap exception punya `__init__` sendiri yang menyimpan data konteks (misalnya `kekurangan` pada `PembayaranKurangError`) lalu memanggil `super().__init__(pesan)`. Data konteks ini berguna bagi pemanggil. Contohnya, program utama bisa langsung menampilkan berapa rupiah yang masih kurang tanpa harus mengolah teks pesan error. Atribut `kode_aturan` juga ikut disimpan supaya kelihatan aturan mana yang dilanggar.

---

## 3. Perubahan setter dan method

Waktu UTS, sebenarnya setter kami sudah menolak nilai yang tidak valid. Tapi setelah ditinjau ulang, masih ada beberapa kekurangan:

- Sebagian setter belum mengecek tipe data, jadi kalau diisi teks, errornya muncul dari tempat lain dan pesannya membingungkan.
- Atribut `suhu` pada `Minuman` belum divalidasi sama sekali, jadi nilai seperti `"hangat"` bisa masuk.
- `validasi_harga()` hanya mengembalikan `True` atau `False`, dan nilai `True` ternyata lolos sebagai harga karena di Python `True` dianggap sama dengan `1`.
- `selesaikan()` memakai `ValueError` yang sama untuk semua jenis kesalahan, sehingga pemanggil tidak bisa membedakan pesanan kosong dengan pesanan yang sudah selesai.

Perubahan yang kami lakukan:

- Setiap setter sekarang memunculkan `TypeError` kalau tipe datanya salah dan `ValueError` kalau nilainya di luar aturan. Pesan errornya juga menyebutkan nilai yang diterima supaya lebih mudah dilacak.
- `validasi_harga()` sekarang langsung memunculkan exception, dan nilai bertipe `bool` ditolak.
- `suhu` diubah menjadi property dengan setter yang memvalidasi nilainya.
- `dari_string()` membungkus error saat parsing dengan `raise ValueError(...) from e`, jadi pesannya lebih jelas tetapi penyebab aslinya tetap tersimpan.
- `Pesanan.tambah_item()` dan `Pesanan.selesaikan()` sekarang memunculkan custom exception sesuai aturan bisnis yang dilanggar.
- `selesaikan()` sekarang menerima parameter `uang_dibayar` dan mengembalikan kembalian beserta poin yang didapat.
- `nomor` pada `Pesanan` kami jadikan property read-only supaya tidak bisa diubah dari luar.
- `Kasir.proses_pembayaran()` mencatat jumlah pembayaran yang gagal, lalu meneruskan exception-nya ke pemanggil (re-raise).

Satu prinsip yang kami pegang: kelas domain tidak boleh mencetak pesan error sendiri. Tugasnya cukup memunculkan exception, sedangkan urusan menampilkan pesan ke pengguna diserahkan ke program utama.

---

## 4. Program utama

Di blok `if __name__ == "__main__":` kami menyiapkan satu skenario yang berhasil dan lima skenario yang sengaja dibuat gagal. Semua skenario dijalankan lewat fungsi `jalankan_skenario()`, yang di dalamnya ada blok `try`, `except`, `else`, dan `finally`.

| Skenario | Hasil | Exception yang ditangkap |
|----------|-------|--------------------------|
| 1. Pesanan normal (Budi, member) | Berhasil | Tidak ada, masuk ke blok `else` |
| 2. Uang kurang | Gagal | `PembayaranKurangError` |
| 3. Kode menu salah | Gagal | `MenuTidakTersediaError` (berasal dari `KeyError`) |
| 4. Menu sedang habis | Gagal | `MenuTidakTersediaError` |
| 5. Memesan 25 item sekaligus | Gagal | `ValueError` |
| 6. Pesanan dibayar dua kali | Gagal | `PesananSudahSelesaiError` |

Beberapa hal yang kami terapkan di program utama:

- Urutan `except` disusun dari yang paling spesifik ke yang paling umum: `PembayaranKurangError`, lalu `PesananError`, lalu `CoffeeShopError`, dan terakhir `ValueError`/`TypeError`. Kalau urutannya dibalik, exception yang spesifik akan ikut tertangkap oleh blok yang umum dan penanganan khususnya tidak pernah jalan.
- Blok `else` hanya dijalankan kalau transaksi berhasil tanpa error. Blok `finally` selalu dijalankan untuk menampilkan ringkasan kasir, baik transaksinya berhasil maupun gagal.
- `raise ... from` dipakai di `cari_menu()` dan `MenuItem.dari_string()`. Pada skenario 3, penyebab asli (`KeyError`) ikut ditampilkan lewat `e.__cause__`.
- Re-raise dipakai di `Kasir.proses_pembayaran()`.
- Fungsi `cari_menu()` memakai gaya EAFP (*easier to ask forgiveness than permission*). Kode langsung mengambil `katalog[kode]` lalu menangani `KeyError` kalau kodenya tidak ada, alih-alih mengecek `if kode in katalog` terlebih dahulu.

### Contoh output

```
4 menu siap dijual.

=== Skenario 1: pesanan normal ===
Pesanan #1 - Budi [LUNAS]
  2 x Latte = Rp60,000
  1 x Mie Pedas = Rp20,000
  TOTAL = Rp80,000
[BERHASIL] Kembalian Rp20,000, poin didapat 8. Member Budi (poin: 8)
--- Kasir Sari: 1 pesanan, 0 pembayaran gagal ---

=== Skenario 2: uang kurang ===
[DITOLAK AB-09] Uang Rp25,000 kurang dari total Rp30,000
  Minta pelanggan menambah Rp5,000
--- Kasir Sari: 2 pesanan, 1 pembayaran gagal ---

=== Skenario 3: kode menu salah ===
[DITOLAK AB-06] Menu 'MN99' tidak ada di daftar menu
  Penyebab asli: KeyError: 'MN99'
--- Kasir Sari: 3 pesanan, 1 pembayaran gagal ---

=== Skenario 4: menu habis ===
[DITOLAK AB-06] Menu 'MN02' sedang habis
--- Kasir Sari: 4 pesanan, 1 pembayaran gagal ---

=== Skenario 5: jumlah melebihi batas ===
[INPUT TIDAK VALID] ValueError: Jumlah per item harus 1 sampai 20, diterima: 25
--- Kasir Sari: 5 pesanan, 1 pembayaran gagal ---

=== Skenario 6: dibayar dua kali ===
[DITOLAK AB-07] Pesanan #6 sudah selesai, tidak bisa dibayar lagi
--- Kasir Sari: 6 pesanan, 2 pembayaran gagal ---
```

---

## 5. Class diagram (revisi)

Class diagram dari UTS kami tambahkan dengan kelas-kelas exception. Supaya tulisannya tetap terbaca, diagramnya kami pisah menjadi dua gambar, yaitu hierarki exception dan kelas domain. Klik gambarnya untuk melihat ukuran penuh.

Notasi yang dipakai: `+` untuk public, `#` untuk protected, `-` untuk private, dan `{static}` untuk atribut atau method milik kelas. Kotak kuning bertuliskan "raise:" di bagian bawah kelas berisi catatan method mana yang memunculkan exception apa.

| Garis | Arti |
|-------|------|
| Garis dengan segitiga kosong | Generalization (pewarisan) |
| Garis dengan panah terbuka | Association |
| Belah ketupat hitam | Composition |
| Belah ketupat putih | Aggregation |

### 5.1 Hierarki exception

Setiap kelas exception diberi stereotype `«exception»` dan terhubung lewat relasi generalization ke base exception `CoffeeShopError`.

[![Hierarki exception](docs/class_diagram_exception.png)](docs/class_diagram_exception.png)

### 5.2 Kelas domain

[![Kelas domain](docs/class_diagram_domain.png)](docs/class_diagram_domain.png)

### 5.3 Diagram lengkap

Versi yang menggabungkan kedua bagian dalam satu gambar bisa dilihat di [docs/class_diagram_lengkap.png](docs/class_diagram_lengkap.png).

Diagram ini dibuat dengan Graphviz, dan file sumbernya (`*.dot`) ada di folder `docs/`. Kalau ada perubahan, gambarnya bisa dibuat ulang dengan perintah:

```bash
dot -Tpng -Gdpi=200 docs/class_diagram_domain.dot -o docs/class_diagram_domain.png
```

### Ringkasan method yang memunculkan exception

| Kelas | Method / setter | Exception |
|-------|-----------------|-----------|
| `MenuItem` | `harga` (setter), `validasi_harga()` | `TypeError`, `ValueError` |
| `MenuItem` | `dari_string()` | `ValueError` (dirantai dari `ValueError` saat parsing) |
| `Minuman` | `ukuran`, `suhu` (setter) | `ValueError` |
| `Makanan` | `level_pedas` (setter) | `TypeError`, `ValueError` |
| `Pelanggan` | `nama` (setter) | `TypeError`, `ValueError` |
| `PoinMixin` | `tambah_poin()` | `TypeError`, `ValueError` |
| `ItemPesanan` | `jumlah` (setter) | `TypeError`, `ValueError` |
| `Pesanan` | `__init__()` | `TypeError` |
| `Pesanan` | `tambah_item()` | `PesananSudahSelesaiError`, `MenuTidakTersediaError`, `TypeError` |
| `Pesanan` | `selesaikan()` | `PesananSudahSelesaiError`, `PesananKosongError`, `TypeError`, `PembayaranKurangError` |
| `Kasir` | `proses_pembayaran()` | Re-raise `CoffeeShopError` |
| Program utama | `cari_menu()` | `MenuTidakTersediaError` (dirantai dari `KeyError`) |
