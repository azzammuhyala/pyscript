[`<- Back`](../index.md)

# Tuple
Tuple adalah objek sequence yang immutable. Sintaks dari tuple cukup mirip di Python dimana menggunakan kurung kurawal `()` diisi beberapa element yang dipisahkan peritem dengan koma `,`. Perlu di ketahui saat mengisi element tuple yang teridiri dari 1 element maka diharuskan untuk memberi koma di akhir element agar konteksnya adalah tuple bukan bagian prioritas dari kurung kurawal.

Berikut ini adalah bagaimana membuat objek tuple secara sintaks:
<pre><span style="color:#8CDCFE">myTuple</span><span style="color:#D4D4D4"> = </span><span style="color:#FFD705">(</span><span style="color:#B5CEA8">1</span><span style="color:#D4D4D4">, </span><span style="color:#B5CEA8">2</span><span style="color:#D4D4D4">, </span><span style="color:#B5CEA8">3</span><span style="color:#FFD705">)</span><br><span style="color:#8CDCFE">mySingleTuple</span><span style="color:#D4D4D4"> = </span><span style="color:#FFD705">(</span><span style="color:#B5CEA8">1</span><span style="color:#D4D4D4">,</span><span style="color:#FFD705">)</span><span style="color:#D4D4D4"> </span><span style="color:#549952"># berikan tanda koma untuk 1 element tuple</span><br><span style="color:#8CDCFE">myEmptyTuple</span><span style="color:#D4D4D4"> = </span><span style="color:#FFD705">()</span></pre>

Sebenarnya tanda kurung kurawal `()` optional, misalnya jika anda menulis `1,` artinya sama dengan `(1,)`. Tapi ini hanya berlaku pada unpack variable, `extends`, `return`, dan `delete`. Berhati-hati lah dengan koma karena bagian ini sulit di temui bugnya!