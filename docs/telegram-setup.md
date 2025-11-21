# Konfigurasi Telegram Bot

Panduan lengkap untuk mengkonfigurasi bot Telegram Anda melalui BotFather.

## 1. Bot Commands (Menu Commands)

Bot commands memungkinkan pengguna melihat daftar perintah yang tersedia dengan mengetik `/` di chat. Konfigurasi ini dilakukan melalui BotFather.

### Cara Mengatur Bot Commands

1. Buka Telegram dan cari **@BotFather**
2. Kirim perintah: `/setcommands`
3. Pilih bot Anda: `@AIPembukuanbot`
4. Kirim daftar commands berikut:

```
start - Mulai bot dan tampilkan menu utama
health - Cek status bot, database, dan Redis
```

### Atau gunakan script otomatis

```bash
python scripts/setup_telegram_commands.py
```

## 2. Bot Description

### Short Description (Deskripsi Singkat)

Ditampilkan di hasil pencarian bot.

**Cara mengatur:**

1. Buka @BotFather
2. Kirim: `/setdescription`
3. Pilih bot Anda
4. Kirim deskripsi:

```
Asisten keuangan pribadi AI dengan persona JARVIS. Catat pemasukan/pengeluaran, lihat ringkasan keuangan, dan dapatkan insight AI.
```

### Full Description (Deskripsi Lengkap)

Ditampilkan di halaman info bot.

**Cara mengatur:**

1. Buka @BotFather
2. Kirim: `/setabouttext`
3. Pilih bot Anda
4. Kirim deskripsi lengkap:

```
🤖 FinancialAssist - AI Financial Assistant Bot

Fitur:
• 💰 Pencatatan transaksi (pemasukan & pengeluaran)
• 📊 Ringkasan keuangan dan laporan
• 🤖 AI insights dengan persona JARVIS
• 🧭 Navigasi yang mudah dan intuitif

Bot ini membantu Anda mengelola keuangan pribadi dengan mudah melalui Telegram.
```

## 3. Bot Picture

**Cara mengatur:**

1. Buka @BotFather
2. Kirim: `/setuserpic`
3. Pilih bot Anda
4. Kirim foto yang ingin digunakan sebagai profil bot

## 4. Bot Settings Lainnya

### Privacy Mode

Jika bot akan digunakan di grup:

1. Buka @BotFather
2. Kirim: `/setprivacy`
3. Pilih bot Anda
4. Pilih mode:
   - **Disable** - Bot dapat membaca semua pesan di grup
   - **Enable** - Bot hanya merespons perintah yang dimulai dengan `/`

**Rekomendasi:** Enable (untuk privasi)

### Group Settings

Jika bot akan digunakan di grup:

1. Buka @BotFather
2. Kirim: `/setjoingroups`
3. Pilih bot Anda
4. Pilih: **Enable** atau **Disable**

## 5. Verifikasi Konfigurasi

Setelah mengkonfigurasi, verifikasi dengan:

```bash
python scripts/verify_telegram_setup.py
```

Atau manual:

1. Buka bot di Telegram: @AIPembukuanbot
2. Ketik `/` untuk melihat commands
3. Cek deskripsi bot di halaman info

## 6. Troubleshooting

### Commands tidak muncul

- Pastikan sudah mengatur via @BotFather
- Tunggu beberapa detik untuk update
- Restart bot jika perlu

### Bot tidak merespons

- Cek apakah bot sedang running: `ps aux | grep src.bot.main`
- Cek logs bot untuk error
- Verifikasi token bot di `.env`

### Bot tidak bisa join grup

- Pastikan `/setjoingroups` sudah di-enable
- Pastikan bot bukan admin di grup tersebut

## 7. Best Practices

1. **Commands**: Buat commands yang jelas dan mudah diingat
2. **Description**: Jelaskan fitur utama bot dengan singkat
3. **Privacy**: Aktifkan privacy mode untuk keamanan
4. **Testing**: Test semua commands setelah konfigurasi
