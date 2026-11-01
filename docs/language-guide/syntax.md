# Syntax
Berikut ini adalah beberapa daftar sintaks dari bahasa pemprograman PyScript. Disini Anda akan mempelajari beberapa
sintaks yang ada di PyScript secara garis besar.

Pada halaman ini, Anda akan diperkenalkan beberapa bentuk sintaks umum yang akan sering muncul di beberapa cabang
pembahasan sintaks lain.

## Komentar
Komentar membantu untuk menjelaskan alur kerja kode dan memberikan beberapa catatan untuk pengembangan kode kedepannya.
Komentar di awali dengan tanda pagar `#` dan berakhir pada akhir baris.

Bentuk sintaks:
<div class="pys-code"><pre><span class="c-comment"># Kode program Hello World untuk pemula</span><span class="c-default"><br><br></span><span class="c-identifier-function">print</span><span class="c-brackets-0">(</span><span class="c-string">&#x27;Hello World!&#x27;</span><span class="c-brackets-0">)</span><span class="c-default"> </span><span class="c-comment"># mencetak kata &quot;Hello World!&quot; ke terminal</span><span class="c-default"><br></span><span class="c-identifier-function">print</span><span class="c-brackets-0">(</span><span class="c-number">1</span><span class="c-default"> + </span><span class="c-number">1</span><span class="c-brackets-0">)</span><span class="c-default">          </span><span class="c-comment"># ini menghasilkan 2 di terminal</span></pre></div>

## Blok Kode
Blok kode di PyScript di awali dengan kurung kurawal `{}` untuk menuliskan beberapa statement. Selain itu, juga dapat
berupa titik koma `;` sebagai statement kosong atau bagian kode yang belum selesai. Kemudian juga bisa berupa satu
statement atau ekspresi tunggal yang bisa ditulis tanpa kurung kurawal dengan catatan bahwa ia hanya menangkap satu buah
statement saja.

Bentuk sintaks:
<div class="pys-code"><pre><span class="c-comment"># untuk statement lebih dari 1</span><span class="c-default"><br></span><span class="c-keyword-constant">func</span><span class="c-default"> </span><span class="c-identifier-function">add</span><span class="c-brackets-0">(</span><span class="c-identifier">a</span><span class="c-default">, </span><span class="c-identifier">b</span><span class="c-brackets-0">)</span><span class="c-default"> </span><span class="c-brackets-0">{</span><span class="c-default"><br></span><span class="c-default">    </span><span class="c-identifier">result</span><span class="c-default"> = </span><span class="c-identifier">a</span><span class="c-default"> + </span><span class="c-identifier">b</span><span class="c-default"><br></span><span class="c-default">    </span><span class="c-keyword">return</span><span class="c-default"> </span><span class="c-identifier">result</span><span class="c-default"><br></span><span class="c-brackets-0">}</span><span class="c-default"><br><br></span><span class="c-comment"># untuk statement tunggal atau sederhana</span><span class="c-default"><br></span><span class="c-keyword-constant">func</span><span class="c-default"> </span><span class="c-identifier-function">sub</span><span class="c-brackets-0">(</span><span class="c-identifier">a</span><span class="c-default">, </span><span class="c-identifier">b</span><span class="c-brackets-0">)</span><span class="c-default"><br></span><span class="c-default">    </span><span class="c-keyword">return</span><span class="c-default"> </span><span class="c-identifier">a</span><span class="c-default"> - </span><span class="c-identifier">b</span><span class="c-default"><br><br></span><span class="c-comment"># statement kosong atau belum selesai</span><span class="c-default"><br></span><span class="c-keyword-constant">func</span><span class="c-default"> </span><span class="c-identifier-function">matmul</span><span class="c-brackets-0">(</span><span class="c-identifier-constant">A</span><span class="c-default">, </span><span class="c-identifier-constant">B</span><span class="c-brackets-0">)</span><span class="c-default">;</span></pre></div>