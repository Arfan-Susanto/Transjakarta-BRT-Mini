# Transjakarta BRT Mini

Website simulasi pencarian rute halte Transjakarta menggunakan algoritma Dijkstra dan Depth-First Search (DFS). Aplikasi membandingkan hasil kedua algoritma berdasarkan data Koridor 2, 4, dan 5C. Proyek ini dibuat untuk demonstrasi teori graf, bukan layanan resmi Transjakarta.

## Spesifikasi

- **Backend:** Python dengan Flask
- **Antarmuka:** HTML, CSS, dan JavaScript dalam satu template
- **Visualisasi graf:** NetworkX dan Matplotlib
- **Data:** 115 ruas jarak antarhalte dengan 60 halte unik, tersimpan di `data/jarak_halte_cleaned.csv`
- **Algoritma:**
  - **Dijkstra** mencari rute dengan total jarak terpendek berdasarkan bobot jarak dalam meter.
  - **DFS** mencari jalur dengan penelusuran mendalam. Jalur yang ditemukan belum tentu paling pendek.
- **Hasil per algoritma:** total jarak dalam kilometer, jumlah ruas, jumlah perpindahan koridor, jumlah halte yang dikunjungi selama pencarian, serta daftar halte pada rute.
- **Visualisasi:** peta graf jaringan dengan warna untuk setiap koridor, penanda halte penghubung, dan animasi proses pencarian serta jalur yang ditemukan.
- **Tampilan:** responsif untuk layar kecil dan besar. Quicksand dimuat dari Google Fonts sehingga memerlukan koneksi internet. Harabara Mais bersifat opsional.

## Cara menjalankan

Pastikan Python sudah terpasang, lalu jalankan perintah berikut dari folder proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Jika PowerShell tidak mengizinkan aktivasi virtual environment, jalankan `python -m pip install -r requirements.txt` tanpa aktivasi. Setelah server berjalan, buka <http://127.0.0.1:5000> di browser.

Untuk menghentikan server, tekan `Ctrl+C` pada terminal tempat server dijalankan.

## Cara menggunakan

1. Pilih halte asal pada kolom **Dari halte**.
2. Pilih halte tujuan pada kolom **Ke halte**.
3. Tekan **Cari rute** untuk membandingkan hasil Dijkstra dan DFS.
4. Tekan tombol tukar di antara kolom untuk menukar asal dan tujuan.
5. Buka **Lihat halte yang dilewati** pada salah satu hasil untuk melihat urutan halte dan informasi ruasnya.
6. Amati jalur kedua algoritma pada **Peta graf BRT**.

Nilai jarak dihitung dari data pada berkas CSV, bukan estimasi waktu perjalanan atau kondisi lalu lintas. Jika nama halte tidak dikenali oleh API, aplikasi menampilkan pesan kesalahan dan saran nama halte yang mirip jika tersedia.

## API

Endpoint berikut digunakan oleh antarmuka untuk menghitung rute:

```http
POST /api/rute
Content-Type: application/json
```

Contoh isi permintaan:

```json
{
  "asal": "Cililitan",
  "tujuan": "Galunggung"
}
```

Respons berisi hasil `dijkstra` dan `dfs`. Masing-masing hasil mencakup jalur (`path`), urutan halte yang diperiksa (`urutan`), rincian ruas (`segmen`), jarak total (`km`), jumlah ruas (`ruas`), perpindahan koridor (`pindah`), dan halte yang dikunjungi (`dikunjungi`). Hasil DFS juga memuat `lebih_persen` jika jaraknya lebih jauh daripada hasil Dijkstra. Permintaan dengan halte yang tidak ditemukan mengembalikan status HTTP 400 dan pesan kesalahan.

Endpoint tambahan:

- `GET /` menampilkan halaman utama.
- `GET /graph.png` mengirim gambar graf jaringan.

## Font opsional

Harabara Mais tidak disertakan dalam proyek. Jika memiliki berkas font tersebut dan lisensinya mengizinkan penggunaan, simpan sebagai `static/fonts/HarabaraMais.ttf` atau `static/fonts/HarabaraMais.otf`. Tanpa font ini, judul menggunakan Quicksand sebagai pengganti.

## Struktur proyek

```text
app.py
data/
  jarak_halte_cleaned.csv
static/
  logo.png
  fonts/
templates/
  index.html
requirements.txt
```
