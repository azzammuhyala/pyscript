"use strict";(()=>{var y=["__debug__","False","None","True","and","class","constructor","extends","func","function","false","global","in","instanceof","is","not","nil","none","null","of","or","true","typeof"],h=["as","assert","break","case","catch","continue","default","del","delete","do","elif","else","elseif","except","finally","for","from","if","import","match","raise","repeat","return","switch","throw","try","until","while","with"],R=["ArithmeticError","AssertionError","AttributeError","BaseException","BaseExceptionGroup","BlockingIOError","BrokenPipeError","BufferError","BytesWarning","ChildProcessError","ConnectionAbortedError","ConnectionError","ConnectionRefusedError","ConnectionResetError","DeprecationWarning","EOFError","EncodingWarning","EnvironmentError","Exception","ExceptionGroup","FileExistsError","FileNotFoundError","FloatingPointError","FutureWarning","GeneratorExit","IOError","ImportCycleError","ImportError","ImportWarning","IndexError","InterruptedError","IsADirectoryError","KeyError","KeyboardInterrupt","LookupError","MemoryError","ModuleNotFoundError","NameError","NotADirectoryError","NotImplementedError","OSError","OverflowError","PendingDeprecationWarning","PermissionError","ProcessLookupError","PythonFinalizationError","RecursionError","ReferenceError","ResourceWarning","RuntimeError","RuntimeWarning","StopAsyncIteration","StopIteration","SyntaxError","SyntaxWarning","SystemError","SystemExit","TimeoutError","TypeError","UnboundLocalError","UnicodeDecodeError","UnicodeEncodeError","UnicodeError","UnicodeTranslateError","UnicodeWarning","UserWarning","ValueError","Warning","WindowsError","ZeroDivisionError","bool","bytearray","bytes","classmethod","complex","dict","enumerate","filter","float","frozendict","frozenset","int","list","map","memoryview","object","property","range","reversed","set","slice","staticmethod","str","super","tuple","type","zip"],T=["abs","aiter","all","anext","any","ascii","bin","breakpoint","callable","ce","chr","comprehension","copyright","credits","decrement","delattr","dir","divmod","eval","exec","exit","format","getattr","globals","hasattr","hash","help","hex","id","increment","input","isinstance","isobjectof","issubclass","iter","len","license","locals","max","min","nce","next","oct","open","ord","pow","print","pyimport","quit","repr","require","round","setattr","sorted","sum","unpack","vars"],q=y.concat(h).join("|"),i="[0-9](?:_?[0-9])*",$=`(?:[eE][+-]?${i})`,r="[jJiI]?",o="(?:\\$(?:[^\\S\\r\\n]*))?",d="[a-zA-Z_][a-zA-Z0-9_]*",f=`(\\s+)(?!(?:${q})\\b)(${o}${d})\\b`,p="((?:R|r|BR|RB|Br|rB|Rb|bR|br|rb))",a="((?:B|b)?)",u=["pys"],b={start:[{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+"(''')",next:"raw_string_apostrophe_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+'(""")',next:"raw_string_quotation_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:a+"(''')",next:"string_apostrophe_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:a+'(""")',next:"string_quotation_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+"(')",next:"raw_string_apostrophe_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+'(")',next:"raw_string_quotation_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:a+"(')",next:"string_apostrophe_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:a+'(")',next:"string_quotation_single"},{token:["storage.type.number","constant.numeric.bin","storage.type.imaginary.number"],regex:`\\b(0[bB])([01](?:_?[01])*)(${r})\\b`},{token:["storage.type.number","constant.numeric.oct","storage.type.imaginary.number"],regex:`\\b(0[oO])([0-7](?:_?[0-7])*)(${r})\\b`},{token:["storage.type.number","constant.numeric.hex","storage.type.imaginary.number"],regex:`\\b(0[xX])([0-9a-fA-F](?:_?[0-9a-fA-F])*)(${r})\\b`},{token:["constant.numeric.float","storage.type.imaginary.number"],regex:`(?<![\\w.])((?:(?:${i})?\\.${i}|${i}\\.)${$}?)(${r})(?![\\w.])`},{token:["constant.numeric.float","storage.type.imaginary.number"],regex:`\\b(${i}${$})(${r})\\b`},{token:["constant.numeric.integer","storage.type.imaginary.number"],regex:`\\b(${i})(${r})\\b`},{token:"comment",regex:/#.*$/},{token:["constant.language","text","storage.type"],regex:"\\b(class)\\b"+f},{token:["constant.language","text","storage.function"],regex:"\\b(func|function)\\b"+f},{token:"keyword.control",regex:`\\b(${h.join("|")})\\b`},{token:"constant.language",regex:`\\b(${y.join("|")})\\b`},{token:"support.type",regex:`${o}\\b(?:${R.join("|")})\\b`},{token:"support.function",regex:`${o}\\b(?:${T.join("|")})\\b`},{token:"function",regex:`${o}\\b${d}\\b(?=\\s*\\()`},{token:"constant.variable",regex:`${o}\\b(?:[A-Z_]*[A-Z][A-Z0-9_]*)\\b`},{token:"variable",regex:`${o}\\b${d}\\b`},{token:"punctuation.operator",regex:/[\(\),;\[\]{}]|\\$/},{token:"keyword.operator",regex:"\\.\\.\\.|&&|\\*\\*|\\+\\+|--|//|<<|==|>>|\\?\\?|\\|\\||!=|%=|&=|\\*=|\\+=|-=|/=|:=|<=|>=|@=|^=|\\|=|~=|\\*\\*=|//=|<<=|>>=|->|=>|!>|~!|<>|[!%&\\*\\+\\-\\./:<=>\\?@^\\|~]"},{token:"invalid.illegal",regex:/\\./},{token:"invalid.illegal",regex:/\$(?:[^\S\r\n]*).?/}],raw_string_apostrophe_triple:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/'''/,next:"start"},{defaultToken:"string.quoted.triple"}],raw_string_quotation_triple:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/"""/,next:"start"},{defaultToken:"string.quoted.triple"}],string_apostrophe_triple:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/'''/,next:"start"},{defaultToken:"string.quoted.triple"}],string_quotation_triple:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/"""/,next:"start"},{defaultToken:"string.quoted.triple"}],raw_string_apostrophe_single:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/,next:"raw_string_apostrophe_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/'/,next:"start"},{defaultToken:"string.quoted.single"}],raw_string_quotation_single:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/,next:"raw_string_quotation_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/"/,next:"start"},{defaultToken:"string.quoted.single"}],string_apostrophe_single:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/,next:"string_apostrophe_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/'/,next:"start"},{defaultToken:"string.quoted.single"}],string_quotation_single:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/,next:"string_quotation_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/"/,next:"start"},{defaultToken:"string.quoted.single"}],"raw-string-escapes":[{token:"string",regex:/\\["'\\]/}],"string-escapes":[{token:"constant.character.escape",regex:/\\[nrtbfav"'\\]/},{token:"constant.character.escape.octal",regex:/\\[0-7]{1,3}/},{token:"constant.character.escape.hex",regex:/\\x[0-9A-Fa-f]{2}/},{token:"constant.character.escape.unicode",regex:/\\u[0-9A-Fa-f]{4}/},{token:"constant.character.escape.unicode",regex:/\\U[0-9A-Fa-f]{8}/},{token:"constant.character.escape.unicode-name",regex:/\\N\{[^}]+\}/},{token:"invalid.illegal.escape",regex:/\\./}]};var k=`snippet __debug__
	__debug__

snippet False
	False

snippet None
	None

snippet True
	True

snippet and
	and

snippet as
	as

snippet assert
	assert \${0:condition}

snippet break
	break

snippet case
	case \${1:condition}:
		\${0:# code}

snippet catch
	catch (\${1:e}) {
		\${0:# code}
	}

snippet class
	class \${1:ClassName} {
		constructor(\${2:parameter}) {
			\${0:# code}
		}
	}

snippet continue
	continue

snippet constructor
	constructor(\${1:parameter}) {
		\${0:# code}
	}

snippet default
	default:

snippet del
	del \${0:target}

snippet delete
	delete \${0:target}

snippet do
	do {
		\${0:# code}
	} while (\${1:condition})

snippet elif
	elif (\${1:condition}) {
		\${0:# code}
	}

snippet else
	else {
		\${0:# code}
	}

snippet elseif
	elseif (\${1:condition}) {
		\${0:# code}
	}

snippet except
	except (\${1:e}) {
		\${0:# code}
	}

snippet extends
	extends \${0:OtherClass}

snippet false
	false

snippet finally
	finally {
		\${0:# code}
	}

snippet for
	for (\${1:i = 0; i < 10; i++}) {
		\${0:# code}
	}

snippet from
	from \${1:moduleName} import \${0:packages}

snippet func
	func \${1:functionName}(\${2:parameter}) {
		\${0:# code}
	}

snippet function
	function \${1:functionName}(\${2:parameter}) {
		\${0:# code}
	}

snippet global
	global \${0:variable}

snippet if
	if (\${1:condition}) {
		\${0:# code}
	}

snippet import
	import \${0:moduleName}

snippet in
	in

snippet instanceof
	instanceof

snippet is
	is

snippet match
	match \${1:target }{
		\${2:condition}: \${3:value}
		default: \${4:defaultValue}
	}

snippet nil
	nil

snippet none
	none

snippet null
	null

snippet not
	not $0

snippet true
	true

snippet typeof
	typeof \${0:target}

snippet of
	of

snippet or
	or

snippet raise
	raise \${0:Exception}

snippet repeat
	repeat {
		\${0:# code}
	} until (\${1:condition})

snippet return
	return

snippet switch
	switch (\${1:target}) {
		case \${2:condition}:
			\${3:# code}
		default:
			\${4:# code}
	}

snippet throw
	throw \${0:Exception}

snippet try
	try {
		\${1:# code}
	} catch (e) {
		\${2:# code}
	}

snippet until
	until (\${0:condition})

snippet while
	while (\${1:condition}) {
		\${0:# code}
	}

snippet with
	with (\${1:contextObject as context}) {
		\${0:# code}
	}

snippet ArithmeticError
	ArithmeticError

snippet AssertionError
	AssertionError

snippet AttributeError
	AttributeError

snippet BaseException
	BaseException

snippet BaseExceptionGroup
	BaseExceptionGroup

snippet BlockingIOError
	BlockingIOError

snippet BrokenPipeError
	BrokenPipeError

snippet BufferError
	BufferError

snippet BytesWarning
	BytesWarning

snippet ChildProcessError
	ChildProcessError

snippet ConnectionAbortedError
	ConnectionAbortedError

snippet ConnectionError
	ConnectionError

snippet ConnectionRefusedError
	ConnectionRefusedError

snippet ConnectionResetError
	ConnectionResetError

snippet DeprecationWarning
	DeprecationWarning

snippet EOFError
	EOFError

snippet Ellipsis
	Ellipsis

snippet EncodingWarning
	EncodingWarning

snippet EnvironmentError
	EnvironmentError

snippet Exception
	Exception

snippet ExceptionGroup
	ExceptionGroup

snippet FileExistsError
	FileExistsError

snippet FileNotFoundError
	FileNotFoundError

snippet FloatingPointError
	FloatingPointError

snippet FutureWarning
	FutureWarning

snippet GeneratorExit
	GeneratorExit

snippet IOError
	IOError

snippet ImportCycleError
	ImportCycleError

snippet ImportError
	ImportError

snippet ImportWarning
	ImportWarning

snippet IndexError
	IndexError

snippet InterruptedError
	InterruptedError

snippet IsADirectoryError
	IsADirectoryError

snippet KeyError
	KeyError

snippet KeyboardInterrupt
	KeyboardInterrupt

snippet LookupError
	LookupError

snippet MemoryError
	MemoryError

snippet ModuleNotFoundError
	ModuleNotFoundError

snippet NameError
	NameError

snippet NotADirectoryError
	NotADirectoryError

snippet NotImplemented
	NotImplemented

snippet NotImplementedError
	NotImplementedError

snippet OSError
	OSError

snippet OverflowError
	OverflowError

snippet PendingDeprecationWarning
	PendingDeprecationWarning

snippet PermissionError
	PermissionError

snippet ProcessLookupError
	ProcessLookupError

snippet PythonFinalizationError
	PythonFinalizationError

snippet RecursionError
	RecursionError

snippet ReferenceError
	ReferenceError

snippet ResourceWarning
	ResourceWarning

snippet RuntimeError
	RuntimeError

snippet RuntimeWarning
	RuntimeWarning

snippet StopAsyncIteration
	StopAsyncIteration

snippet StopIteration
	StopIteration

snippet SyntaxError
	SyntaxError

snippet SyntaxWarning
	SyntaxWarning

snippet SystemError
	SystemError

snippet SystemExit
	SystemExit

snippet TimeoutError
	TimeoutError

snippet TypeError
	TypeError

snippet UnboundLocalError
	UnboundLocalError

snippet UnicodeDecodeError
	UnicodeDecodeError

snippet UnicodeEncodeError
	UnicodeEncodeError

snippet UnicodeError
	UnicodeError

snippet UnicodeTranslateError
	UnicodeTranslateError

snippet UnicodeWarning
	UnicodeWarning

snippet UserWarning
	UserWarning

snippet ValueError
	ValueError

snippet Warning
	Warning

snippet WindowsError
	WindowsError

snippet ZeroDivisionError
	ZeroDivisionError

snippet abs
	abs($0)

snippet aiter
	aiter($0)

snippet all
	all($0)

snippet anext
	anext($0)

snippet any
	any($0)

snippet ascii
	ascii($0)

snippet bin
	bin($0)

snippet bool
	bool

snippet breakpoint
	breakpoint()

snippet bytearray
	bytearray

snippet bytes
	bytes

snippet callable
	callable($0)

snippet ce
	ce($0)

snippet chr
	chr($0)

snippet classmethod
	classmethod

snippet complex
	complex

snippet comprehension
	comprehension($0)

snippet copyright
	copyright()

snippet credits
	credits()

snippet decrement
	decrement($0)

snippet delattr
	delattr($0)

snippet dict
	dict

snippet dir
	dir($0)

snippet divmod
	divmod($0)

snippet enumerate
	enumerate($0)

snippet eval
	eval($0)

snippet exec
	exec($0)

snippet exit
	exit($0)

snippet filter
	filter($0)

snippet float
	float

snippet format
	format($0)

snippet frozenset
	frozenset

snippet frozendict
	frozendict

snippet getattr
	getattr($0)

snippet globals
	globals()

snippet hasattr
	hasattr($0)

snippet hash
	hash($0)

snippet help
	help($0)

snippet hex
	hex($0)

snippet id
	id($0)

snippet increment
	increment($0)

snippet inf
	inf

snippet infj
	infj

snippet input
	input($0)

snippet int
	int

snippet isinstance
	isinstance($0)

snippet isobjectof
	isobjectof($0)

snippet issubclass
	issubclass($0)

snippet iter
	iter($0)

snippet len
	len($0)

snippet license
	license()

snippet list
	list($0)

snippet locals
	locals()

snippet map
	map($0)

snippet max
	max($0)

snippet memoryview
	memoryview

snippet min
	min($0)

snippet nce
	nce($0)

snippet next
	next($0)

snippet nan
	nan

snippet nanj
	nanj

snippet object
	object

snippet oct
	oct($0)

snippet open
	open($0)

snippet ord
	ord($0)

snippet pow
	pow($0)

snippet print
	print($0)

snippet property
	property

snippet pyimport
	pyimport($0)

snippet quit
	quit($0)

snippet range
	range($0)

snippet repr
	repr($0)

snippet require
	require($0)

snippet reversed
	reversed($0)

snippet round
	round($0)

snippet set
	set

snippet setattr
	setattr($0)

snippet slice
	slice

snippet sorted
	sorted($0)

snippet staticmethod
	staticmethod

snippet str
	str

snippet sum
	sum($0)

snippet super
	super($0)

snippet tuple
	tuple

snippet type
	type

snippet unpack
	unpack($0)

snippet vars
	vars($0)

snippet zip
	zip($0)

snippet fl
	for (i of range($1)) {
		$0
	}

snippet fe
	for (item of \${1:iterableObject}) {
		$0
	}

snippet lambda
	func(\${1:parameter}) => \${0:returnValue}

snippet future
	from __future__ import \${0:futureName}
`;var c={$schema:"https://acode.app/schema/plugin/v0.1.0.json",id:"acode.plugin.pyscript",name:"PyScript",main:"src/main.js",version:"1.0.2",repository:"https://github.com/azzammuhyala/pyscript",icon:"PyScript.png",minVersionCode:290,license:"MIT",keywords:["pyscript","pyslang","pys","programming","language","programming language","highlight"],price:0,permissions:[],author:{name:"AzzamMuhyala",email:"azzammuhyala@gmail.com",github:"azzammuhyala"}};var m=class{async init(t,e,n){e.id=c.id;let _=t+"PyScript.png";this.iconStyle=document.createElement("style"),this.iconStyle.textContent=`
        .file_type_pyscript::before {
            display: inline-block;
            content: '';
            background-image: url(${_});
            background-size: contain;
            background-repeat: no-repeat;
            height: 1em;
            width: 1em;
        }`,document.head.append(this.iconStyle),ace.define("ace/mode/pyscript",function(E,w,B){let v=E("ace/mode/text").Mode,F=E("ace/mode/text_highlight_rules").TextHighlightRules;class I extends F{constructor(){super(),this.$rules=b,this.normalizeRules()}}class W extends v{constructor(){super(),this.HighlightRules=I;let l=this.getTokenizer(),P=l.getLineTokens.bind(l),S=["string_apostrophe_single","string_quotation_single","raw_string_apostrophe_single","raw_string_quotation_single"];l.getLineTokens=function(x,M){let g=P(x,M);return S.includes(g.state)&&!x.endsWith("\\")&&(g.state="start"),g}}}w.Mode=W}),aceModes.addMode("pyscript",u,"PyScript"),this.snippet=snippetManager.parseSnippetFile(k),snippetManager.register(this.snippet,"pyscript"),editorManager.editor.setOptions({enableBasicAutocompletion:!0,enableSnippets:!0,enableLiveAutocompletion:!0}),this.toPyscript=()=>this.updateActiveFile("pyscript"),editorManager.on("switch-file",this.toPyscript),editorManager.on("rename-file",this.toPyscript),this.updateAllFiles("pyscript")}async destroy(){editorManager.off("switch-file",this.toPyscript),editorManager.off("rename-file",this.toPyscript),this.iconStyle.remove(),this.updateAllFiles("text"),aceModes.removeMode("pyscript"),snippetManager.unregister(this.snippet,"pyscript")}applyPluginToFile(t,e){if(!t)return;let n=url.extname(t.name);u.includes(n.startsWith(".")?n.slice(1):n)&&t.session.setMode(`ace/mode/${e}`)}updateActiveFile(t){this.applyPluginToFile(editorManager.activeFile,t),editorManager.emit("update")}updateAllFiles(t){for(let e of editorManager.files)this.applyPluginToFile(e,t);editorManager.emit("update")}},z=async()=>{for(;!window.acode||!window.ace||!window.editorManager||!window.acode.setPluginInit||!window.acode.setPluginUnmount||!window.acode.require||!window.ace.require||document.readyState==="loading";)await new Promise(s=>setTimeout(s,250))};z().then(()=>{window.url=acode.require("url"),window.aceModes=acode.require("aceModes"),window.snippetManager=ace.require("ace/snippets").snippetManager;let s=new m;acode.setPluginInit(c.id,async(t,e,n)=>{await s.init(t.endsWith("/")?t:t+"/",e,n)}),acode.setPluginUnmount(c.id,async()=>{await s.destroy()})});})();
