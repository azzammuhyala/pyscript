[`<- Back`](../index.md)

# breakpoint
`breakpoint()` adalah sebuah fungsi yang digunakan untuk menghentikan sementara runtime dan memasuki shell debugging.
Shell debugging ini dapat dipakai untuk melihat nilai-nilai variable dan meeksekusi kode didalamnya secara langsung.
Shell debugging mirip dengan shell REPL biasa, sama-sama bisa menjalankan kode perbagian akan tetapi ini khusus untuk
membantu debugging.

Saat `breakpoint()` dijalankan, akan diberikan informasi seperti letak file dan baris fungsi di panggil serta scope nama
contextnya, contohnya seperti ini:
<pre><span style="color:#D4D4D4">&gt; pyscript.pys(1)&lt;program&gt;<br><span style="color:#800080">(Pdb) </span></pre>

Disini, Anda dapat meinspeksi nilai-nilai variable yang ada dalam scope breakpoint di panggil. Misalnya pada kode ini:
<pre><span style="color:#307CD6">func</span><span style="color:#D4D4D4"> </span><span style="color:#DCDCAA">add</span><span style="color:#FFD705">(</span><span style="color:#8CDCFE">a</span><span style="color:#D4D4D4">, </span><span style="color:#8CDCFE">b</span><span style="color:#FFD705">)</span><span style="color:#D4D4D4"> </span><span style="color:#FFD705">{</span><br><span style="color:#D4D4D4">    </span><span style="color:#8CDCFE">result</span><span style="color:#D4D4D4"> = </span><span style="color:#8CDCFE">a</span><span style="color:#D4D4D4"> + </span><span style="color:#8CDCFE">b</span><br><span style="color:#D4D4D4">    </span><span style="color:#DCDCAA">breakpoint</span><span style="color:#D45DBA">()</span><br><span style="color:#D4D4D4">    </span><span style="color:#C586C0">return</span><span style="color:#D4D4D4"> </span><span style="color:#8CDCFE">result</span><br><span style="color:#FFD705">}</span><br><br><span style="color:#8CDCFE">a</span><span style="color:#D4D4D4"> = </span><span style="color:#B5CEA8">1</span><br><span style="color:#8CDCFE">b</span><span style="color:#D4D4D4"> = </span><span style="color:#B5CEA8">1</span><br><br><span style="color:#8CDCFE">result</span><span style="color:#D4D4D4"> = </span><span style="color:#DCDCAA">add</span><span style="color:#FFD705">(</span><span style="color:#8CDCFE">a</span><span style="color:#D4D4D4">, </span><span style="color:#8CDCFE">b</span><span style="color:#FFD705">)</span><br><span style="color:#DCDCAA">print</span><span style="color:#FFD705">(</span><span style="color:#8CDCFE">result</span><span style="color:#FFD705">)</span></pre>

Saat kode tersebut diesekusi, Anda mendapati tampilan seperti ini:
<pre><span style="color:#D4D4D4">&gt; pyscript.pys(3)add<br><span style="color:#800080">(Pdb) </span></pre>

Dari situ, Anda bisa melihat nilai dari variable dalam scope lokal `add` atau global dengan menuliskan nama variablenya.
<pre><span style="color:#D4D4D4">&gt; pyscript.pys(3)add<br><span style="color:#800080">(Pdb) </span>result<br>2</pre>

Dengan fungsi `locals()` atau `dir()` (tanpa argument) Anda bisa melihat semua isi scope variable di lokal.
<pre><span style="color:#800080">(Pdb) </span>locals()<br>{'a': 1, 'b': 1, 'result': 2}<br><span style="color:#800080">(Pdb) </span>dir()<br>['a', 'b', 'result']</pre>

Selain itu, Anda bisa mengedit atau menghapus (dengan statement `del` / `delete`) beberapa variable didalamnya.
<pre><span style="color:#800080">(Pdb) </span>result = 11<br>11<br><span style="color:#800080">(Pdb) </span>result<br>11</pre>

Untuk keluar dari shell, ketik perintah `c` atau `continue` maka shell akan keluar dan kode dapat dijalankan kembali.
<pre>11</pre>

Karena tadi dalam shell kita mengubah nilai variable `result` menjadi `11`, lalu statemen `return` mengembalikan nilai
dari variable `result` maka akhir kode menjadi `11` bukan `2`.

Ada beberapa perintah di shell breakpoint yang tersedia, ketik `h` atau `help` untuk melihat list perintah yang
tersedia saat dalam shell.
<pre><span style="color:#800080">(Pdb) </span>h<br><br>Documented commands:<br>====================<br>(c)ontinue          : Exit the debugger and continue the program.<br>(d)own [count]      : Decrease the scope level (default one) to the older frame.<br>(h)elp              : Show this help display.<br>(l)ine              : Show the position where breakpoint() was called.<br>(q)uit / exit [code]: Exit the interpreter by throwing SystemExit.<br>(u)p [count]        : Increase the scope level (default one) to the older frame.<br><br></pre>