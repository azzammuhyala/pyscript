# PyScript📖
PyScript adalah bahasa pemprograman yang mengabungkan sintaks Python dan JavaScript.

## Cara menjalankan?
1. Anda perlu interpreter / aplikasi Python (usahakan paling terbaru) di [website resmi](https://python.org).
2. Setelah itu coba jalankan file `pys.py` dengan Python (`py/python pys.py`). (dibutuhkan folder `pyscript/`)
3. Jika sudah harusnya Anda akan melihat shell dari PyScript yang mirip dengan Python.
4. Untuk menjalankan file PyScript cukup sertakan argumen file yang mau dijalankan dengan `py/python pys.py file.pys`

## Contoh-contoh kode
Anda bisa lihat dan coba eksekusi semua contoh file kodenya di `examples/`

## Sintaks
Anda bisa kustom bahasa ini dengan bahasa sesuka Anda! Bukan berati grammarnya tapi hanya nama kata kunci dan nama builtins. Tetapi tidak mengubah bahasa dari output, misalnya pesan error atau pesan lain. Untuk mekustomnya Anda bisa mengubah isi file JSON `pyscript/syntax.pys.json`, disitu ada 2 kategori berupa object/dict berupa `"keywords"` dan `"builtins"`. kunci dari data adalah nama asli dari 2 kategori, kemudian nilainya adalah nama kustom dari nama asli. Misalnya:
```json
{
    "keywords": {
        "and": "dan",
        "break": "hentikan",
        "case": "kasus",
        "catch": "tangkap",
        "continue": "lanjutkan",
        "default": "bawaan",
        ... // Lanjutkan
    },
    "builtins": {
        "abs": "mutlak",
        "aiter": "aiterator",
        "all": "semua",
        "anext": "anext",
        "any": "ada",
        ... // Lanjutkan
    }
}
```

Semua file sintaks sudah disediakan di folder `syntax/`, Ada beberapa bahasa yang bisa anda coba dengan menyalin datanya lalu tempel di `pyscript/syntax.pys.json` dengan nama sama persis `syntax.pys.json`!

Untuk grammar sintaksnya bisa Anda cek di `examples/`.

## Bug
Jika Anda menemukan bug Anda bisa beritahu Saya di repositori ini!