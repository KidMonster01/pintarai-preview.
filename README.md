# PintarAI v2.1 — Go Live Preview

Website responsif + PWA Student App + backend FastAPI + SQLite *draft* + konfigurasi Docker/Render.

**Mulai di `GO_LIVE.md`.** Paket dapat dijalankan lokal dan siap dideploy oleh pemilik repo/hosting, tetapi **belum dipublikasikan online**.

## Ringkasan keamanan
- `PINTARAI_SITE_MODE=production` adalah *default aman*: menutup `/app/` pada server, karena HTML masih berisi 148 materi draft dan 296 soal yang belum lolos validasi.
- `PINTARAI_SITE_MODE=preview` membuka PWA demo, dengan peringatan permanen bahwa materinya belum diverifikasi.
- `render.yaml` meminta `PINTARAI_PREVIEW_PASSWORD` melalui secret prompt ketika membuat Blueprint agar `/app/` hanya bisa dibuka penguji. Password disetel hanya sebagai environment variable; browser memunculkan dialog HTTP Basic. Pada lokal boleh tidak di-set.
- API konten draft tetap tertutup kecuali `PINTARAI_DEMO_PREVIEW=1` diaktifkan secara sengaja.
- Progres belajar dan chat demo hanya di browser; tidak ada akun atau penyimpanan identitas siswa pada server.
- File data SQLite server sementara; jangan gunakan untuk data pengguna yang harus persisten.

## Struktur
- `web/` landing page, halaman privasi preview, PWA di `web/app/`
- `backend/` FastAPI dan SQLite seed
- `data/` konten draft + audit contoh
- `verification-v1.9/` mesin verifikasi dari versi lama (belum aktif live)
- `android-source/` sumber WebView lama, bukan APK
- `render.yaml`, `Dockerfile`, `GO_LIVE.md` untuk deploy
- `scripts/smoke_test.py` untuk cek endpoint setelah deploy
- `tests/` pengujian lokal

Uji lokal: `PINTARAI_SITE_MODE=preview python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` setelah `pip install -r backend/requirements.txt`.
