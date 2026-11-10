# Language Guide

Seperti yang sudah di singgung sebelumnya, PyScript adalah gabungan sintaks dari berbagai bahasa salah satunya Python,
dan JavaScript. Sebelum mempelajari panduan bahasa ini, Anda perlu memahami tentang bahasa pemprograman Python terlebih
dahulu dikarenakan bahasa ini berkaitan erat langsung dengan bahasa pemprograman Python.

Di PyScript, semua objek adalah objek Python, jadi nilai `1`, `3.141`, `'Hello'`, `set()`, `[2, 3, 5]` merupakan objek
Python. Tidak ada objek PyScript yang mewakili nilai-nilai tersebut terkecuali beberapa objek salah satunya fungsi.
Fungsi di PyScript merupakan kelas dari `pyscript.core.pystypes.PysFunction`. Kadang beberapa builtins PyScript
dibungkus oleh kelas tersebut seperti `pyscript.core.pystypes.PysPythonFunction`,
`pyscript.core.pystypes.PysBuiltinFunction`, atau `pyscript.core.pystypes.PysPrinter` (bukan turunan dari
`PysFunction`).

Selain itu, PyScript juga mendukung penuh pustaka di luar PyScript atau yang ditulis di Python seperti contohnya SymPy,
NumPy, PyGame, OpenCV, dll. Anda bisa meimpornya seperti pada Python dengan statemen atau kata kunci `import`/`from`
maupun lewat fungsi builtin `pyimport()`.

<div class="pys-code"><pre><span class="c-keyword">import</span><span class="c-default"> </span><span class="c-identifier">numpy</span><span class="c-default"> </span><span class="c-keyword">as</span><span class="c-default"> </span><span class="c-identifier">np</span><span class="c-default"><br><br></span><span class="c-keyword">from</span><span class="c-default"> </span><span class="c-identifier">sympy</span><span class="c-default"> </span><span class="c-keyword">import</span><span class="c-default"> *</span><span class="c-default"><br><br></span><span class="c-identifier">pyg</span><span class="c-default"> = </span><span class="c-identifier-function">pyimport</span><span class="c-brackets-0">(</span><span class="c-string">&#x27;pygame&#x27;</span><span class="c-brackets-0">)</span></pre></div>