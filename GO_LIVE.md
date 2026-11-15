# Panduan Go Live PintarAI v2.1 — PREVIEW (Indonesia)

**Belum online secara otomatis.** Paket ini siap dikirim ke Git repository dan dideploy ke Render. Tindakan di akun Git/hosting tetap harus dilakukan pemilik akun. **Ini BUKAN rilis produksi akademik.**

## 1) Uji lokal (Windows/Mac/Linux)

1. Ekstrak ZIP, buka terminal pada folder yang berisi `render.yaml`.
2. Instal Python 3.12 (atau versi modern kompatibel), lalu:
   ```sh
   python -m pip install -r backend/requirements.txt
   ```
3. Agar Student App dapat dibuka, set mode preview:
   - Windows PowerShell: `$env:PINTARAI_SITE_MODE="preview"`
   - macOS/Linux: `export PINTARAI_SITE_MODE=preview`
4. Jalankan: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
5. Buka:
   - Website: `http://127.0.0.1:8000/`
   - Student App PWA: `http://127.0.0.1:8000/app/`
   - Status API: `http://127.0.0.1:8000/api/v1/status`
   - Audit: `http://127.0.0.1:8000/api/v1/quality`

Untuk mode produksi, unset `PINTARAI_SITE_MODE` atau set `production`; URL `/app/` akan tertutup (503) sampai konten terverifikasi tersedia dan build app publik tanpa draft dibuat.

## 2) Deploy versi Preview di Render

1. Buat repo GitHub pribadi baru (belum perlu domain). Masukkan isi folder proyek ini **ke root** repo, termasuk `Dockerfile` dan `render.yaml`. **Jangan masukkan `.env` atau API key.**
2. Buka https://dashboard.render.com/, pilih **New > Blueprint**, sambungkan repo yang tadi dibuat, dan jalankan konfigurasi `render.yaml`.
3. Pastikan nilai `PINTARAI_SITE_MODE=preview`; `PINTARAI_DEMO_PREVIEW=0` (API tidak membuka draft). **Masukkan password unik ketika Render Blueprint meminta `PINTARAI_PREVIEW_PASSWORD`** (tidak perlu menaruhnya dalam file atau mengirim lewat chat). Setelah deploy, browser meminta kredensial HTTP Basic saat mengakses `/app/`. Username boleh diisi `tester`, password sesuai yang kamu set.
4. Tunggu status **Live**, lalu buka URL `<nama-layanan>.onrender.com` yang **ditunjukkan** di dashboard (jangan menebak URL).
5. Periksa `/api/v1/health`, `/api/v1/quality`, `/`, dan `/app/` (masukkan kata sandi yang kamu set saat diminta).
6. Untuk memasang di Android, buka `/app/` lewat HTTPS lalu menu browser → **Instal aplikasi**. Ini PWA, bukan APK di Play Store.
7. Bila punya domain sendiri, tambahkan melalui pengaturan Custom Domains Render, lalu ikuti catatan DNS yang Render berikan. HTTPS biasanya dikelola penyedia hosting.

**Batas Render Free:** service bisa sleep saat idle, startup awal lambat, filesystem sementara. Database SQLite v2.1 hanya memuat *data draft contoh* pada startup dan **tidak** menyimpan data pengguna ke server; ini cukup untuk demo, bukan data siswa/operasional nyata. Untuk pengguna sesungguhnya gunakan database persisten, backup, akun, keamanan anak, dan layanan berbayar sesuai kebutuhan.

## 3) Menguji setelah deploy

```sh
python scripts/smoke_test.py https://URL-YANG-DIBERIKAN-RENDER
```

Skrip membaca `health`, `quality`, `status`, dan situs; tidak melakukan perubahan data. Karena default Blueprint mengaktifkan password, pemeriksaan `/app/` mengharapkan 401 (akses privat); gunakan `--preview` hanya untuk instalasi preview yang memang tanpa password.

## 4) Release gate / keselamatan

- v2.1 masih 148 **materi draft**, 296 **soal draft**, 0 approved. Data demo tertanam di HTML Student App.
- API default *fail-closed*, dan produksi memblokir `/app/` secara server-side. **Jangan menjadikan preview sebagai layanan pendidikan siap pakai.**
- Tidak ada OpenAI API key, verifikasi AI live, autentikasi akun, atau backend chat real yang aktif.
- Isi demo berasal dari materi orisinal yang masih perlu pengecekan; belum ada jaminan akurasi 100%.
- Sebelum publikasi kepada siswa, lakukan pengujian perangkat, penilaian risiko, kontrol keamanan anak, kebijakan privasi resmi, validasi materi otomatis berbasis bukti, hak penggunaan, serta monitoring.

## 5) Mengaktifkan perangkat Android

`android-source/` merupakan *source project* lama dari v2.0 yang masih disertakan untuk kontinuitas, bukan APK rilis. Cara tercepat mencoba aplikasi installable sekarang adalah PWA. APK native/Play Store perlu Android Studio dan proses build/signing serta pengujian tersendiri.
