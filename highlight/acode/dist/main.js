"use strict";(()=>{var _=["__debug__","False","None","True","and","class","constructor","extends","func","function","false","global","in","instanceof","is","not","nil","none","null","of","or","true","typeof"],w=["as","assert","break","case","catch","continue","default","del","delete","do","elif","else","elseif","except","finally","for","from","if","import","match","raise","repeat","return","switch","throw","try","until","while","with"],T=["ArithmeticError","AssertionError","AttributeError","BaseException","BaseExceptionGroup","BlockingIOError","BrokenPipeError","BufferError","BytesWarning","ChildProcessError","ConnectionAbortedError","ConnectionError","ConnectionRefusedError","ConnectionResetError","DeprecationWarning","EOFError","EncodingWarning","EnvironmentError","Exception","ExceptionGroup","FileExistsError","FileNotFoundError","FloatingPointError","FutureWarning","GeneratorExit","IOError","ImportCycleError","ImportError","ImportWarning","IndexError","InterruptedError","IsADirectoryError","KeyError","KeyboardInterrupt","LookupError","MemoryError","ModuleNotFoundError","NameError","NotADirectoryError","NotImplementedError","OSError","OverflowError","PendingDeprecationWarning","PermissionError","ProcessLookupError","PythonFinalizationError","RecursionError","ReferenceError","ResourceWarning","RuntimeError","RuntimeWarning","StopAsyncIteration","StopIteration","SyntaxError","SyntaxWarning","SystemError","SystemExit","TimeoutError","TypeError","UnboundLocalError","UnicodeDecodeError","UnicodeEncodeError","UnicodeError","UnicodeTranslateError","UnicodeWarning","UserWarning","ValueError","Warning","WindowsError","ZeroDivisionError","bool","bytearray","bytes","classmethod","complex","dict","enumerate","filter","float","frozendict","frozenset","int","list","map","memoryview","object","property","range","reversed","set","slice","staticmethod","str","super","tuple","type","zip"],q=["abs","aiter","all","anext","any","ascii","bin","breakpoint","callable","ce","chr","comprehension","copyright","credits","decrement","delattr","dir","divmod","eval","exec","exit","format","getattr","globals","hasattr","hash","help","hex","id","increment","input","isinstance","isobjectof","issubclass","iter","len","license","locals","max","min","nce","next","oct","open","ord","pow","print","pyimport","quit","repr","require","round","setattr","sorted","sum","unpack","vars"],M=_.concat(w).join("|"),r="[0-9](?:_?[0-9])*",b=`(?:[eE][+-]?${r})`,e="[jJiI]?",i="(?:\\$(?:[^\\S\\r\\n]*))?",u="[a-zA-Z_][a-zA-Z0-9_]*",k=`(\\s+)(?!(?:${M})\\b)(${i}${u})\\b`,s="((?:R|r|BR|RB|Br|rB|Rb|bR|br|rb))",p="((?:B|b)?)",I=["pys"],v={start:[{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:s+"(''')",next:"raw_string_apostrophe_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:s+'(""")',next:"raw_string_quotation_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+"(''')",next:"string_apostrophe_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+'(""")',next:"string_quotation_triple"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:s+"(')",next:"raw_string_apostrophe_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:s+'(")',next:"raw_string_quotation_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+"(')",next:"string_apostrophe_single"},{token:["storage.type.string.prefix","punctuation.definition.string.begin"],regex:p+'(")',next:"string_quotation_single"},{token:["storage.type.number","constant.numeric.bin","storage.type.imaginary.number"],regex:`\\b(0[bB])([01](?:_?[01])*)(${e})\\b`},{token:["storage.type.number","constant.numeric.oct","storage.type.imaginary.number"],regex:`\\b(0[oO])([0-7](?:_?[0-7])*)(${e})\\b`},{token:["storage.type.number","constant.numeric.hex","storage.type.imaginary.number"],regex:`\\b(0[xX])([0-9a-fA-F](?:_?[0-9a-fA-F])*)(${e})\\b`},{token:["constant.numeric.float","storage.type.imaginary.number"],regex:`\\b((?:(?:${r})?\\.${r}|${r}\\.)${b}?)(${e})\\b`},{token:["constant.numeric.float","storage.type.imaginary.number"],regex:`\\b(${r}${b})(${e})\\b`},{token:["constant.numeric.integer","storage.type.imaginary.number"],regex:`\\b(${r})(${e})\\b`},{token:"comment",regex:/#.*$/},{token:["constant.language","text","storage.type"],regex:"\\b(class)\\b"+k},{token:["constant.language","text","storage.function"],regex:"\\b(func|function)\\b"+k},{token:"keyword.control",regex:`\\b(${w.join("|")})\\b`},{token:"constant.language",regex:`\\b(${_.join("|")})\\b`},{token:"support.type",regex:`${i}\\b(?:${T.join("|")})\\b`},{token:"support.function",regex:`${i}\\b(?:${q.join("|")})\\b`},{token:"function",regex:`${i}\\b${u}\\b(?=\\s*\\()`},{token:"constant.variable",regex:`${i}\\b(?:[A-Z_]*[A-Z][A-Z0-9_]*)\\b`},{token:"variable",regex:`${i}\\b${u}\\b`},{token:"punctuation.operator",regex:/[\(\),;\[\]{}]|\\$/},{token:"keyword.operator",regex:"\\.\\.\\.|&&|\\*\\*|\\+\\+|--|//|<<|==|>>|\\?\\?|\\|\\||!=|%=|&=|\\*=|\\+=|-=|/=|:=|<=|>=|@=|^=|\\|=|~=|\\*\\*=|//=|<<=|>>=|->|=>|!>|~!|<>|[!%&\\*\\+\\-\\./:<=>\\?@^\\|~]"},{token:"invalid.illegal",regex:/\\./},{token:"invalid.illegal",regex:/\$(?:[^\S\r\n]*).?/}],raw_string_apostrophe_triple:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/'''/,next:"start"},{defaultToken:"string.quoted.triple"}],raw_string_quotation_triple:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/"""/,next:"start"},{defaultToken:"string.quoted.triple"}],string_apostrophe_triple:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/'''/,next:"start"},{defaultToken:"string.quoted.triple"}],string_quotation_triple:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/},{token:"punctuation.definition.string.end",regex:/"""/,next:"start"},{defaultToken:"string.quoted.triple"}],raw_string_apostrophe_single:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/,next:"raw_string_apostrophe_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/'/,next:"start"},{defaultToken:"string.quoted.single"}],raw_string_quotation_single:[{include:"raw-string-escapes"},{token:"string",regex:/\\$/,next:"raw_string_quotation_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/"/,next:"start"},{defaultToken:"string.quoted.single"}],string_apostrophe_single:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/,next:"string_apostrophe_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/'/,next:"start"},{defaultToken:"string.quoted.single"}],string_quotation_single:[{include:"string-escapes"},{token:"constant.character.escape",regex:/\\$/,next:"string_quotation_single"},{token:"invalid.illegal.unclosed-string",regex:/$/,next:"start"},{token:"punctuation.definition.string.end",regex:/"/,next:"start"},{defaultToken:"string.quoted.single"}],"raw-string-escapes":[{token:"string",regex:/\\["'\\]/}],"string-escapes":[{token:"constant.character.escape",regex:/\\[nrtbfav"'\\]/},{token:"constant.character.escape.octal",regex:/\\[0-7]{1,3}/},{token:"constant.character.escape.hex",regex:/\\x[0-9A-Fa-f]{2}/},{token:"constant.character.escape.unicode",regex:/\\u[0-9A-Fa-f]{4}/},{token:"constant.character.escape.unicode",regex:/\\U[0-9A-Fa-f]{8}/},{token:"constant.character.escape.unicode-name",regex:/\\N\{[^}]+\}/},{token:"invalid.illegal.escape",regex:/\\./}]};var W=`snippet __debug__
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
`;var a={$schema:"https://acode.app/schema/plugin/v0.1.0.json",id:"acode.plugin.pyscript",name:"PyScript",main:"src/main.js",version:"1.0.1",repository:"https://github.com/azzammuhyala/pyscript",icon:"PyScript.png",minVersionCode:290,license:"MIT",keywords:["pyscript","pyslang","pys","programming","language","programming language","highlight"],price:0,permissions:[],author:{name:"Azzam Muhyala",email:"azzammuhyala@gmail.com",github:"azzammuhyala"}};var m=class{async init(n,t,c){if(!c.firstInit)return;this.destroyed=!1,t.id=a.id;let E=n+"PyScript.png";acode.addIcon("pyscript-icon",E),this.iconStyle=document.createElement("style"),this.iconStyle.textContent=`
        .file_type_pyscript::before {
            display: inline-block;
            content: '';
            background-image: url(${E});
            background-size: contain;
            background-repeat: no-repeat;
            height: 1em;
            width: 1em;
        }`,document.head.append(this.iconStyle),ace.define("ace/mode/pyscript",function(l,S,B){let $=l("ace/lib/oop"),x=l("ace/mode/text").Mode,F=l("ace/mode/text_highlight_rules").TextHighlightRules,f=function(){this.$rules=v,this.normalizeRules()};$.inherits(f,F);let y=function(){x.call(this),this.HighlightRules=f;let g=this.getTokenizer(),A=g.getLineTokens.bind(g),R=["string_apostrophe_single","string_quotation_single","raw_string_apostrophe_single","raw_string_quotation_single"];g.getLineTokens=function(h,P){let d=A(h,P);return R.includes(d.state)&&!h.endsWith("\\")&&(d.state="start"),d}};$.inherits(y,x),S.Mode=y}),aceModes.addMode("pyscript",I,"PyScript"),this.snippet=snippetManager.parseSnippetFile(W),snippetManager.register(this.snippet,"pyscript"),editorManager.editor.setOptions({enableBasicAutocompletion:!0,enableSnippets:!0,enableLiveAutocompletion:!0}),this.updateSession("pyscript")}async destroy(){this.updateSession("text"),this.iconStyle.remove(),aceModes.removeMode("pyscript"),snippetManager.unregister(this.snippet,"pyscript"),this.destroyed=!0}applyPluginToFile(n){url.extname(n.name)===".pys"&&n.session.setMode("ace/mode/pyscript")}updateSession(n){if(!this.destroyed){for(let t of editorManager.files)!t||!t.name||this.applyPluginToFile(t);editorManager.emit("update")}}},z=async()=>{for(;!window.acode||!window.ace||!window.editorManager||!window.acode.setPluginInit||!window.acode.setPluginUnmount||!window.acode.require||!window.ace.require||document.readyState==="loading";)await new Promise(o=>setTimeout(o,250))};z().then(()=>{window.url=acode.require("url"),window.aceModes=acode.require("aceModes"),window.snippetManager=ace.require("ace/snippets").snippetManager;let o=new m;acode.setPluginInit(a.id,async(n,t,c)=>{await o.init(n.endsWith("/")?n:n+"/",t,c)}),acode.setPluginUnmount(a.id,()=>{o.destroy()})});})();
