[`<- Back`](../index.md)

# Function
Di Python, definisi fungsi adalah dengan `def` yang berupa statemen, tapi di PyScript tidak seperti itu. Fungsi dalam PyScript adalah sebuah ekspresi. Definisinya ada 3 kata kunci yakni `func` atau `function` (alias), dan `constructor`. Berikut penjelasannya:

## `func` / `function`
Struktur fungsi terdiri dari nama fungsi (optional), parameter, dan tubuh seperti pada bagian ini:
<pre><span style="color:#307CD6">func</span><span style="color:#D4D4D4"> &lt;function name (OPTIONAL)</span><span style="color:#D4D4D4">&gt;</span><span style="color:#FFD705">(</span><span style="color:#D4D4D4">&lt;parameter&gt;</span><span style="color:#FFD705">)</span><br><body&gt; style="color:#D4D4D4">    &lt;body&gt;</span></pre>

Function name merupakan identifier atau tidak ada (optional), jika nama fungsi tidak diberikan maka fungsi mejadi anonimus yang biasanya dipakai didalam ekspresi.

Parameter fungsi bisa berupa argumen biasa (wajib diisi), atau argumen optional, argumen biasa berupa nama parameter identifier, kalau ingin parameter itu optional untuk diisi maka beri tanda sama dengan `=` setelahnya lalu kemudian nilai default parameter tersebut. Perlu diketahui bahwa evaluasi nilai default pada keyword argumen di eksekusi sekali saat fungsi dibuat.

Body adalah statemen tubuh dari fungsi.

## `constructor`
Struktur constructor terdiri dari parameter dan tubuh saja seperti pada bagian ini:
<pre><span style="color:#307CD6">constructor</span><span style="color:#FFD705">(</span><span style="color:#D4D4D4">&lt;parameter&gt;</span><span style="color:#FFD705">)</span><br><body&gt; style="color:#D4D4D4">    &lt;body&gt;</span></pre>

Apa perbedaanya dengan fungsi biasa? Perbedaanya, constructor dipakai untuk initialisasi fungsi kelas dan hanya bisa dideklarasikan di dalam body class. Artinya, constructor sebenarnya adalah fungsi bernama `__init__` yang memberikan parameter awal bernama `self`.

## Apakah ada parameter dinamis?
Tidak, parameter di Python seperti `*args` ataupun `**kwargs` tidak ada sama sekali dalam sinstaks PyScript agar pengecekan argument lebih cepat.

## Apakah objek fungsi adalah `types.FunctionType`?
Tidak, objek fungsi adalah berasal dari `pyscript.core.objects.PysFunction`, merupakan implementasi fungsi khusus untuk PyScript. Dengan ini, kode PyScript bisa dieksekusi dan dapat membuat jejak traceback.

## Apakah ada fungsi async?
Tidak, dalam PyScript tidak ada teknik async dan await untuk kemudahan implementasi dan kesederhanaan bahasa.

## Apakah fungsi dapat di panggil diluar interpreter PyScript?
Ya, fungsi yang dibuat didalam PyScript bisa dieksekusi di dalam scope Python, `pyscript.core.objects.PysFunction` memiliki metode `__call__` dimana fungsi bisa di panggil di dalam Python. Akan tetapi jejak traceback bisa terputus sehingga akan sulit mencari jejak kesalahan yang terjadi. Jika terjadi kesalahan akan melempar eksekusi `pyscript.core.exceptions.PysSignal`.

## Apakah fungsi immutable?
Tidak, fungsi adalah mutable yang dapat membuat attribut didalam objek fungsi itu.

## Apakah ada dekorator?
Ya, fungsi dapat didekorasi dengan `@` sebelum deklarasi fungsi.