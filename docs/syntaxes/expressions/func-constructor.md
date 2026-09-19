[`<- Back`](../index.md)

# Function
Di Python, definisi fungsi adalah dengan menggunakan kata kunci `def` yang berupa statemen, tetapi di PyScript tidak seperti itu. Fungsi dalam PyScript adalah sebuah ekspresi. Definisinya terdiri dari 3 kata kunci yakni `func` atau `function` (alias), dan `constructor`. Berikut penjelasannya:

## `func` / `function`
Struktur sintaks fungsi terdiri dari nama fungsi (optional), parameter, dan tubuh seperti pada bagian ini:

```
func <function-name (OPTIONAL)>(<parameter>)
    <body>
```

- `function-name` merupakan identifier atau tidak ada (optional). Jika nama fungsi tidak diberikan maka fungsi tersebut menjadi fungsi anonimus (seperti lambda function di Python) yang biasanya dipakai didalam ekspresi atau pun fungsi sekali pakai.

- `parameter` fungsi bisa berupa argumen biasa (wajib diisi), atau argumen optional. Argumen biasa berupa nama parameter identifier, kalau ingin parameter itu optional untuk diisi maka beri tanda sama dengan `=` setelahnya lalu kemudian nilai default parameter tersebut. Perlu diketahui bahwa evaluasi nilai default pada argumen di eksekusi sekali saat fungsi dibuat.

- `body` adalah statemen atau isi dari fungsi. Pelajari lebih lanjut tentang [struktur sintaks body](../index.md).

## `constructor`
Struktur sintaks constructor terdiri dari parameter dan tubuh saja seperti pada bagian ini:

```
constructor(<parameter>)
    <body>
```

Apa perbedaan dengan fungsi biasa? Perbedaanya, constructor dipakai untuk initialisasi fungsi kelas dan hanya bisa dideklarasikan di dalam body class. Artinya, constructor sebenarnya adalah fungsi bernama `__init__` yang memberikan parameter awal bernama `self` (refrensi objek class).

## Apakah objek fungsi adalah `types.FunctionType`?
Tidak, objek fungsi berasal dari `pyscript.core.objects.PysFunction`, kelas ini merupakan implementasi fungsi khusus untuk PyScript. Dengan ini, kode PyScript bisa dieksekusi dan dapat membuat jejak traceback yang informatif.

## Apakah fungsi dapat di panggil diluar interpreter PyScript?
Ya, fungsi yang dibuat didalam PyScript bisa dieksekusi di dalam scope Python. `pyscript.core.objects.PysFunction` memiliki metode `__call__` dimana fungsi bisa di panggil di dalam Python. Akan tetapi jejak traceback akan terputus sehingga akan sulit mencari jejak kesalahan yang terjadi. Jika terjadi kesalahan akan melempar eksepsi `pyscript.core.exceptions.PysSignal`.

## Apakah fungsi immutable?
Tidak, fungsi adalah mutable yang berati dapat menyimpan attribut tambahan ke dalam objek fungsi.

## Apakah dekorator didukung?
Ya, fungsi dapat didekorasi dengan `@` sebelum deklarasi fungsi.

## Apakah ada parameter dinamis?
Penjelasan lebih lanjut ada [disini](../../qna.md#apakah-ada-parameter-dan-argumen-dinamis).

## Apakah ada fungsi async?
Penjelasan lebih lanjut ada [disini](../../qna.md#apakah-ada-fungsi-async).