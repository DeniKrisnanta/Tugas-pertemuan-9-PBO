"""
Sistem Kasir Coffee Shop
Proyek UTS PBO + Exception Handling

Aturan bisnis (AB-xx) dijelaskan di README.md.
"""


# =====================================================================
# HIERARKI CUSTOM EXCEPTION
# =====================================================================

class CoffeeShopError(Exception):
    """Base exception aplikasi: semua pelanggaran aturan bisnis kasir."""

    def __init__(self, pesan, kode_aturan=None):
        super().__init__(pesan)
        self.kode_aturan = kode_aturan        # konteks: aturan bisnis yang dilanggar


class MenuTidakTersediaError(CoffeeShopError):
    """AB-06: menu tidak ada di daftar menu atau sedang habis."""

    def __init__(self, kode_menu, alasan="tidak ada di daftar menu"):
        self.kode_menu = kode_menu            # konteks
        self.alasan = alasan                  # konteks
        super().__init__(f"Menu '{kode_menu}' {alasan}", "AB-06")


class PesananError(CoffeeShopError):
    """Kelompok error yang berkaitan dengan status sebuah pesanan."""

    def __init__(self, pesan, nomor_pesanan, kode_aturan=None):
        self.nomor_pesanan = nomor_pesanan    # konteks
        super().__init__(pesan, kode_aturan)


class PesananKosongError(PesananError):
    """AB-08: pesanan tanpa item tidak boleh dibayar."""

    def __init__(self, nomor_pesanan):
        super().__init__(
            f"Pesanan #{nomor_pesanan} masih kosong, belum bisa dibayar",
            nomor_pesanan, "AB-08")


class PesananSudahSelesaiError(PesananError):
    """AB-07: pesanan yang sudah dibayar tidak boleh diubah atau dibayar lagi."""

    def __init__(self, nomor_pesanan, aksi):
        self.aksi = aksi                      # konteks: aksi yang ditolak
        super().__init__(
            f"Pesanan #{nomor_pesanan} sudah selesai, tidak bisa {aksi}",
            nomor_pesanan, "AB-07")


class PembayaranKurangError(CoffeeShopError):
    """AB-09: uang yang dibayarkan harus minimal sebesar total pesanan."""

    def __init__(self, total, dibayar):
        self.total = total                    # konteks
        self.dibayar = dibayar                # konteks
        self.kekurangan = total - dibayar     # konteks
        super().__init__(
            f"Uang Rp{dibayar:,} kurang dari total Rp{total:,}", "AB-09")


# =====================================================================
# FUNGSI BANTU VALIDASI
# =====================================================================

def _wajib_angka(nilai, nama_field):
    """TypeError jika bukan int/float (bool ditolak karena True == 1)."""
    if isinstance(nilai, bool) or not isinstance(nilai, (int, float)):
        raise TypeError(f"{nama_field} harus berupa angka, bukan {type(nilai).__name__}")


def _wajib_int(nilai, nama_field):
    """TypeError jika bukan bilangan bulat (bool ditolak)."""
    if isinstance(nilai, bool) or not isinstance(nilai, int):
        raise TypeError(f"{nama_field} harus bilangan bulat, bukan {type(nilai).__name__}")


# =====================================================================
# KELAS DOMAIN
# =====================================================================

class MenuItem:
    jumlah_menu = 0                                   # class attribute

    def __init__(self, kode, nama, harga):
        self._kode = kode                             # protected
        self._nama = nama                             # protected
        self.__harga = 0                              # private
        self.harga = harga                            # lewat setter (validasi)
        self.__tersedia = True                        # private
        MenuItem.jumlah_menu += 1

    @property
    def kode(self):
        return self._kode

    @property
    def nama(self):
        return self._nama

    @property
    def harga(self):
        return self.__harga

    @harga.setter
    def harga(self, nilai):                           # AB-01
        self.__harga = MenuItem.validasi_harga(nilai)

    @property
    def tersedia(self):
        return self.__tersedia

    def tandai_habis(self):
        self.__tersedia = False

    def tandai_tersedia(self):
        self.__tersedia = True

    @staticmethod
    def validasi_harga(nilai):
        """Dulu mengembalikan True/False, sekarang memunculkan exception."""
        _wajib_angka(nilai, "Harga")
        if nilai <= 0:
            raise ValueError(f"Harga harus lebih dari 0, diterima: {nilai}")
        return nilai

    @classmethod
    def dari_string(cls, teks):                       # alternative constructor
        try:
            kode, nama, harga = teks.split("|")
            harga = int(harga)
        except ValueError as e:                       # jumlah bagian salah / harga bukan angka
            raise ValueError(
                f"Format menu salah: {teks!r} (contoh benar: 'MN01|Latte|22000')"
            ) from e
        return cls(kode, nama, harga)

    def hitung_harga(self):
        return self.__harga

    def __str__(self):
        return f"{self._kode} - {self._nama} (Rp{self.hitung_harga():,})"

    def __repr__(self):
        return f"{type(self).__name__}({self._kode!r}, {self._nama!r}, {self.__harga})"

    def __eq__(self, other):
        return isinstance(other, MenuItem) and self._kode == other._kode

    def __hash__(self):
        return hash(self._kode)


class Minuman(MenuItem):
    TAMBAHAN_UKURAN = {"S": 0, "M": 3000, "L": 6000}  # class attribute
    SUHU_VALID = ("panas", "dingin")                  # class attribute

    def __init__(self, kode, nama, harga, ukuran="M", suhu="panas"):
        super().__init__(kode, nama, harga)
        self.__ukuran = "M"
        self.ukuran = ukuran
        self.__suhu = "panas"
        self.suhu = suhu

    @property
    def ukuran(self):
        return self.__ukuran

    @ukuran.setter
    def ukuran(self, nilai):                          # AB-02
        if nilai not in Minuman.TAMBAHAN_UKURAN:
            raise ValueError(f"Ukuran harus S, M, atau L, diterima: {nilai!r}")
        self.__ukuran = nilai

    @property
    def suhu(self):
        return self.__suhu

    @suhu.setter
    def suhu(self, nilai):                            # AB-02 (dulu belum divalidasi)
        if nilai not in Minuman.SUHU_VALID:
            raise ValueError(f"Suhu harus 'panas' atau 'dingin', diterima: {nilai!r}")
        self.__suhu = nilai

    def hitung_harga(self):                           # override
        total = super().hitung_harga() + Minuman.TAMBAHAN_UKURAN[self.__ukuran]
        if self.__suhu == "dingin":
            total += 2000
        return total

    def __str__(self):
        return f"{super().__str__()} [{self.__ukuran}, {self.__suhu}]"


class Makanan(MenuItem):
    def __init__(self, kode, nama, harga, level_pedas=0):
        super().__init__(kode, nama, harga)
        self.__level_pedas = 0
        self.level_pedas = level_pedas

    @property
    def level_pedas(self):
        return self.__level_pedas

    @level_pedas.setter
    def level_pedas(self, nilai):                     # AB-03
        _wajib_int(nilai, "Level pedas")
        if not (0 <= nilai <= 5):
            raise ValueError(f"Level pedas harus 0 sampai 5, diterima: {nilai}")
        self.__level_pedas = nilai

    def hitung_harga(self):                           # override
        total = super().hitung_harga()
        if self.__level_pedas >= 4:
            total += 2000
        return total

    def __str__(self):
        return f"{super().__str__()} [pedas {self.__level_pedas}]"


class PoinMixin:
    def __init__(self):
        super().__init__()
        self.__poin = 0

    @property
    def poin(self):
        return self.__poin

    def tambah_poin(self, jumlah):                    # AB-10
        _wajib_int(jumlah, "Poin")
        if jumlah < 0:
            raise ValueError(f"Poin tidak boleh negatif, diterima: {jumlah}")
        self.__poin += jumlah


class Pelanggan:
    def __init__(self, nama):
        super().__init__()
        self.__nama = ""
        self.nama = nama

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):                            # AB-04
        if not isinstance(nilai, str):
            raise TypeError(f"Nama harus berupa teks, bukan {type(nilai).__name__}")
        if not nilai.strip():
            raise ValueError("Nama pelanggan tidak boleh kosong")
        self.__nama = nilai.strip()

    def proses_pembelian(self, total):
        return 0                                      # pelanggan biasa: tanpa poin

    def __str__(self):
        return f"Pelanggan {self.__nama}"


class Member(Pelanggan, PoinMixin):                   # multiple inheritance + mixin
    def proses_pembelian(self, total):                # override
        poin_baru = int(total // 10000)
        self.tambah_poin(poin_baru)
        return poin_baru

    def __str__(self):
        return f"Member {self.nama} (poin: {self.poin})"


class ItemPesanan:
    def __init__(self, menu, jumlah):
        self.__menu = menu                            # association ke MenuItem
        self.__jumlah = 1
        self.jumlah = jumlah

    @property
    def menu(self):
        return self.__menu

    @property
    def jumlah(self):
        return self.__jumlah

    @jumlah.setter
    def jumlah(self, nilai):                          # AB-05
        _wajib_int(nilai, "Jumlah")
        if not (1 <= nilai <= 20):
            raise ValueError(f"Jumlah per item harus 1 sampai 20, diterima: {nilai}")
        self.__jumlah = nilai

    def hitung_subtotal(self):
        return self.__menu.hitung_harga() * self.__jumlah

    def __str__(self):
        return f"{self.__jumlah} x {self.__menu.nama} = Rp{self.hitung_subtotal():,}"


class Pesanan:
    jumlah_pesanan = 0                                # class attribute

    def __init__(self, pelanggan):
        if not isinstance(pelanggan, Pelanggan):
            raise TypeError("Pesanan harus dibuat untuk objek Pelanggan")
        Pesanan.jumlah_pesanan += 1
        self.__nomor = Pesanan.jumlah_pesanan
        self.__pelanggan = pelanggan                  # aggregation (dari luar)
        self.__daftar_item = []                       # composition (dibuat di dalam)
        self.__selesai = False

    @property
    def nomor(self):
        return self.__nomor

    @property
    def selesai(self):
        return self.__selesai

    def tambah_item(self, menu, jumlah):
        if self.__selesai:                                        # AB-07
            raise PesananSudahSelesaiError(self.__nomor, "ditambah item")
        if not isinstance(menu, MenuItem):
            raise TypeError("Item pesanan harus berupa MenuItem")
        if not menu.tersedia:                                     # AB-06
            raise MenuTidakTersediaError(menu.kode, "sedang habis")
        self.__daftar_item.append(ItemPesanan(menu, jumlah))      # AB-05 dicek di ItemPesanan

    def hitung_total(self):
        return sum(item.hitung_subtotal() for item in self.__daftar_item)

    def selesaikan(self, uang_dibayar):
        """Membayar pesanan. Mengembalikan (kembalian, poin_didapat)."""
        if self.__selesai:                                        # AB-07
            raise PesananSudahSelesaiError(self.__nomor, "dibayar lagi")
        if not self.__daftar_item:                                # AB-08
            raise PesananKosongError(self.__nomor)
        _wajib_angka(uang_dibayar, "Uang yang dibayarkan")
        total = self.hitung_total()
        if uang_dibayar < total:                                  # AB-09
            raise PembayaranKurangError(total, uang_dibayar)
        self.__selesai = True
        poin = self.__pelanggan.proses_pembelian(total)
        return uang_dibayar - total, poin

    def __str__(self):
        status = "LUNAS" if self.__selesai else "BELUM BAYAR"
        baris = [f"Pesanan #{self.__nomor} - {self.__pelanggan.nama} [{status}]"]
        baris += [f"  {item}" for item in self.__daftar_item]
        baris.append(f"  TOTAL = Rp{self.hitung_total():,}")
        return "\n".join(baris)


class Kasir:
    def __init__(self, nama):
        self.nama = nama
        self.__daftar_pesanan = []                    # association ke Pesanan
        self.__transaksi_gagal = 0

    @property
    def daftar_pesanan(self):
        return tuple(self.__daftar_pesanan)           # salinan, tidak bisa diubah dari luar

    @property
    def transaksi_gagal(self):
        return self.__transaksi_gagal

    def buat_pesanan(self, pelanggan):
        pesanan = Pesanan(pelanggan)
        self.__daftar_pesanan.append(pesanan)
        return pesanan

    def proses_pembayaran(self, pesanan, uang_dibayar):
        try:
            return pesanan.selesaikan(uang_dibayar)
        except CoffeeShopError:
            self.__transaksi_gagal += 1               # catat dulu...
            raise                                     # ...lalu teruskan ke pemanggil (re-raise)


# =====================================================================
# PROGRAM UTAMA
# =====================================================================

def cari_menu(katalog, kode):
    """Gaya EAFP: langsung ambil dari dict, tangani kalau ternyata tidak ada."""
    try:
        return katalog[kode]
    except KeyError as e:
        raise MenuTidakTersediaError(kode) from e     # exception chaining


def jalankan_skenario(judul, aksi, kasir):
    print(f"\n=== {judul} ===")
    try:
        hasil = aksi()
    except PembayaranKurangError as e:                # paling spesifik
        print(f"[DITOLAK {e.kode_aturan}] {e}")
        print(f"  Minta pelanggan menambah Rp{e.kekurangan:,}")
    except PesananError as e:                         # kelompok error pesanan
        print(f"[DITOLAK {e.kode_aturan}] {e}")
    except CoffeeShopError as e:                      # semua error aplikasi lainnya
        print(f"[DITOLAK {e.kode_aturan}] {e}")
        if e.__cause__ is not None:
            print(f"  Penyebab asli: {type(e.__cause__).__name__}: {e.__cause__}")
    except (ValueError, TypeError) as e:              # data tidak valid dari setter
        print(f"[INPUT TIDAK VALID] {type(e).__name__}: {e}")
    else:                                             # hanya jika tidak ada exception
        print(f"[BERHASIL] {hasil}")
    finally:                                          # selalu dijalankan
        print(f"--- Kasir {kasir.nama}: {len(kasir.daftar_pesanan)} pesanan, "
              f"{kasir.transaksi_gagal} pembayaran gagal ---")


if __name__ == "__main__":
    # Data awal: kalau ada data menu yang salah, program berhenti di sini.
    try:
        katalog = {m.kode: m for m in [
            Minuman("MN01", "Latte", 22000, "L", "dingin"),
            Minuman("MN02", "Americano", 18000, "M", "panas"),
            Makanan("MK01", "Mie Pedas", 18000, 4),
            MenuItem.dari_string("MK02|Croissant|15000"),
        ]}
        budi = Member("Budi")
        andi = Pelanggan("Andi")
    except (ValueError, TypeError) as e:
        print("Data awal tidak valid:", e)
        raise SystemExit(1)
    else:
        print(f"{MenuItem.jumlah_menu} menu siap dijual.")

    katalog["MN02"].tandai_habis()                    # Americano sedang habis
    kasir = Kasir("Sari")

    # Skenario 1 — berhasil
    def pesanan_normal():
        pesanan = kasir.buat_pesanan(budi)
        pesanan.tambah_item(cari_menu(katalog, "MN01"), 2)
        pesanan.tambah_item(cari_menu(katalog, "MK01"), 1)
        kembalian, poin = kasir.proses_pembayaran(pesanan, 100000)
        print(pesanan)
        return f"Kembalian Rp{kembalian:,}, poin didapat {poin}. {budi}"

    # Skenario 2 — gagal: uang kurang
    def uang_kurang():
        pesanan = kasir.buat_pesanan(andi)
        pesanan.tambah_item(cari_menu(katalog, "MN01"), 1)
        return kasir.proses_pembayaran(pesanan, 25000)

    # Skenario 3 — gagal: kode menu tidak ada (raise ... from KeyError)
    def kode_salah():
        pesanan = kasir.buat_pesanan(andi)
        pesanan.tambah_item(cari_menu(katalog, "MN99"), 1)

    # Skenario 4 — gagal: menu sedang habis
    def menu_habis():
        pesanan = kasir.buat_pesanan(andi)
        pesanan.tambah_item(cari_menu(katalog, "MN02"), 1)

    # Skenario 5 — gagal: jumlah melebihi batas (ValueError dari setter)
    def jumlah_berlebih():
        pesanan = kasir.buat_pesanan(andi)
        pesanan.tambah_item(cari_menu(katalog, "MK02"), 25)

    # Skenario 6 — gagal: pesanan dibayar dua kali
    def bayar_dua_kali():
        pesanan = kasir.buat_pesanan(andi)
        pesanan.tambah_item(cari_menu(katalog, "MK02"), 1)
        kasir.proses_pembayaran(pesanan, 20000)
        kasir.proses_pembayaran(pesanan, 20000)

    jalankan_skenario("Skenario 1: pesanan normal", pesanan_normal, kasir)
    jalankan_skenario("Skenario 2: uang kurang", uang_kurang, kasir)
    jalankan_skenario("Skenario 3: kode menu salah", kode_salah, kasir)
    jalankan_skenario("Skenario 4: menu habis", menu_habis, kasir)
    jalankan_skenario("Skenario 5: jumlah melebihi batas", jumlah_berlebih, kasir)
    jalankan_skenario("Skenario 6: dibayar dua kali", bayar_dua_kali, kasir)

    print("\n=== Info tambahan ===")
    print(katalog["MN01"] == MenuItem.dari_string("MN01|Latte|22000"))
    print(katalog["MN01"] == katalog["MK01"])
    print([k.__name__ for k in Member.__mro__])
    print([k.__name__ for k in PesananKosongError.__mro__])
