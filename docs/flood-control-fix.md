# Perbaikan Flood Control Error

## Masalah

Error `telegram.error.RetryAfter: Flood control exceeded. Retry in X seconds` muncul ketika terlalu banyak request ke Telegram API dalam waktu singkat.

## Solusi yang Diimplementasikan

### 1. Helper Function untuk Retry dengan Exponential Backoff

File: `src/bot/utils/telegram_helpers.py`

Fungsi `handle_telegram_retry_after()` secara otomatis:

- Menangkap `RetryAfter` exception
- Menunggu sesuai waktu yang diminta oleh Telegram
- Menambahkan exponential backoff (1s, 2s, 4s, ...)
- Retry hingga 3 kali (default)
- Log warning untuk monitoring

**Contoh penggunaan:**

```python
from src.bot.utils.telegram_helpers import handle_telegram_retry_after

# Otomatis handle flood control
await handle_telegram_retry_after(bot.send_message, chat_id=123, text="Hello")
```

### 2. Perbaikan Script Setup

File: `scripts/setup_telegram_commands.py`

- Menggunakan `handle_telegram_retry_after()` untuk semua Telegram API calls
- Menambahkan delay antara request (1-2 detik)
- Proper error handling dan cleanup

### 3. Rate Limiting Middleware

File: `src/bot/middleware/rate_limiter.py`

- Mencegah abuse dari user
- Menghormati Telegram API limits (30 messages/second)
- Menggunakan Redis untuk production, in-memory untuk development

## Cara Menggunakan

### Untuk Script Setup

```bash
python scripts/setup_telegram_commands.py
```

Script akan otomatis handle flood control dengan retry.

### Untuk Kode Bot

```python
from src.bot.utils.telegram_helpers import handle_telegram_retry_after

# Wrap semua Telegram API calls
result = await handle_telegram_retry_after(
    bot.send_message,
    chat_id=user_id,
    text="Response"
)
```

## Best Practices

1. **Selalu gunakan helper function** untuk Telegram API calls yang mungkin terkena flood control
2. **Tambahkan delay** antara multiple requests (minimal 1 detik)
3. **Monitor logs** untuk flood control warnings
4. **Jangan spam** Telegram API - gunakan rate limiting middleware

## Testing

Test helper function:

```python
from src.bot.utils.telegram_helpers import handle_telegram_retry_after

# Test dengan bot yang valid
result = await handle_telegram_retry_after(bot.get_me)
print(result)
```

## Catatan

- Flood control adalah mekanisme Telegram untuk mencegah abuse
- Normal jika terjadi sesekali, tapi harus di-handle dengan baik
- Exponential backoff membantu mengurangi kemungkinan retry yang gagal
- Rate limiting middleware mencegah flood control dari sisi user
