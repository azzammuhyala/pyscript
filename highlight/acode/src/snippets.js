export const snippets = `snippet __debug__
\t__debug__

snippet False
\tFalse

snippet None
\tNone

snippet True
\tTrue

snippet and
\tand

snippet as
\tas

snippet assert
\tassert \${0:condition}

snippet break
\tbreak

snippet case
\tcase \${1:condition}:
\t\t\${0:# code}

snippet catch
\tcatch (\${1:e}) {
\t\t\${0:# code}
\t}

snippet class
\tclass \${1:ClassName} {
\t\tconstructor(\${2:parameter}) {
\t\t\t\${0:# code}
\t\t}
\t}

snippet continue
\tcontinue

snippet constructor
\tconstructor(\${1:parameter}) {
\t\t\${0:# code}
\t}

snippet default
\tdefault:

snippet del
\tdel \${0:target}

snippet delete
\tdelete \${0:target}

snippet do
\tdo {
\t\t\${0:# code}
\t} while (\${1:condition})

snippet elif
\telif (\${1:condition}) {
\t\t\${0:# code}
\t}

snippet else
\telse {
\t\t\${0:# code}
\t}

snippet elseif
\telseif (\${1:condition}) {
\t\t\${0:# code}
\t}

snippet except
\texcept (\${1:e}) {
\t\t\${0:# code}
\t}

snippet extends
\textends \${0:OtherClass}

snippet false
\tfalse

snippet finally
\tfinally {
\t\t\${0:# code}
\t}

snippet for
\tfor (\${1:i = 0; i < 10; i++}) {
\t\t\${0:# code}
\t}

snippet from
\tfrom \${1:moduleName} import \${0:packages}

snippet func
\tfunc \${1:functionName}(\${2:parameter}) {
\t\t\${0:# code}
\t}

snippet function
\tfunction \${1:functionName}(\${2:parameter}) {
\t\t\${0:# code}
\t}

snippet global
\tglobal \${0:variable}

snippet if
\tif (\${1:condition}) {
\t\t\${0:# code}
\t}

snippet import
\timport \${0:moduleName}

snippet in
\tin

snippet instanceof
\tinstanceof

snippet is
\tis

snippet match
\tmatch \${1:target }{
\t\t\${2:condition}: \${3:value}
\t\tdefault: \${4:defaultValue}
\t}

snippet nil
\tnil

snippet none
\tnone

snippet null
\tnull

snippet not
\tnot \$0

snippet true
\ttrue

snippet typeof
\ttypeof \${0:target}

snippet of
\tof

snippet or
\tor

snippet raise
\traise \${0:Exception}

snippet repeat
\trepeat {
\t\t\${0:# code}
\t} until (\${1:condition})

snippet return
\treturn

snippet switch
\tswitch (\${1:target}) {
\t\tcase \${2:condition}:
\t\t\t\${3:# code}
\t\tdefault:
\t\t\t\${4:# code}
\t}

snippet throw
\tthrow \${0:Exception}

snippet try
\ttry {
\t\t\${1:# code}
\t} catch (e) {
\t\t\${2:# code}
\t}

snippet until
\tuntil (\${0:condition})

snippet while
\twhile (\${1:condition}) {
\t\t\${0:# code}
\t}

snippet with
\twith (\${1:contextObject as context}) {
\t\t\${0:# code}
\t}

snippet ArithmeticError
\tArithmeticError

snippet AssertionError
\tAssertionError

snippet AttributeError
\tAttributeError

snippet BaseException
\tBaseException

snippet BaseExceptionGroup
\tBaseExceptionGroup

snippet BlockingIOError
\tBlockingIOError

snippet BrokenPipeError
\tBrokenPipeError

snippet BufferError
\tBufferError

snippet BytesWarning
\tBytesWarning

snippet ChildProcessError
\tChildProcessError

snippet ConnectionAbortedError
\tConnectionAbortedError

snippet ConnectionError
\tConnectionError

snippet ConnectionRefusedError
\tConnectionRefusedError

snippet ConnectionResetError
\tConnectionResetError

snippet DeprecationWarning
\tDeprecationWarning

snippet EOFError
\tEOFError

snippet Ellipsis
\tEllipsis

snippet EncodingWarning
\tEncodingWarning

snippet EnvironmentError
\tEnvironmentError

snippet Exception
\tException

snippet ExceptionGroup
\tExceptionGroup

snippet FileExistsError
\tFileExistsError

snippet FileNotFoundError
\tFileNotFoundError

snippet FloatingPointError
\tFloatingPointError

snippet FutureWarning
\tFutureWarning

snippet GeneratorExit
\tGeneratorExit

snippet IOError
\tIOError

snippet ImportCycleError
\tImportCycleError

snippet ImportError
\tImportError

snippet ImportWarning
\tImportWarning

snippet IndexError
\tIndexError

snippet InterruptedError
\tInterruptedError

snippet IsADirectoryError
\tIsADirectoryError

snippet KeyError
\tKeyError

snippet KeyboardInterrupt
\tKeyboardInterrupt

snippet LookupError
\tLookupError

snippet MemoryError
\tMemoryError

snippet ModuleNotFoundError
\tModuleNotFoundError

snippet NameError
\tNameError

snippet NotADirectoryError
\tNotADirectoryError

snippet NotImplemented
\tNotImplemented

snippet NotImplementedError
\tNotImplementedError

snippet OSError
\tOSError

snippet OverflowError
\tOverflowError

snippet PendingDeprecationWarning
\tPendingDeprecationWarning

snippet PermissionError
\tPermissionError

snippet ProcessLookupError
\tProcessLookupError

snippet PythonFinalizationError
\tPythonFinalizationError

snippet RecursionError
\tRecursionError

snippet ReferenceError
\tReferenceError

snippet ResourceWarning
\tResourceWarning

snippet RuntimeError
\tRuntimeError

snippet RuntimeWarning
\tRuntimeWarning

snippet StopAsyncIteration
\tStopAsyncIteration

snippet StopIteration
\tStopIteration

snippet SyntaxError
\tSyntaxError

snippet SyntaxWarning
\tSyntaxWarning

snippet SystemError
\tSystemError

snippet SystemExit
\tSystemExit

snippet TimeoutError
\tTimeoutError

snippet TypeError
\tTypeError

snippet UnboundLocalError
\tUnboundLocalError

snippet UnicodeDecodeError
\tUnicodeDecodeError

snippet UnicodeEncodeError
\tUnicodeEncodeError

snippet UnicodeError
\tUnicodeError

snippet UnicodeTranslateError
\tUnicodeTranslateError

snippet UnicodeWarning
\tUnicodeWarning

snippet UserWarning
\tUserWarning

snippet ValueError
\tValueError

snippet Warning
\tWarning

snippet WindowsError
\tWindowsError

snippet ZeroDivisionError
\tZeroDivisionError

snippet abs
\tabs(\$0)

snippet aiter
\taiter(\$0)

snippet all
\tall(\$0)

snippet anext
\tanext(\$0)

snippet any
\tany(\$0)

snippet ascii
\tascii(\$0)

snippet bin
\tbin(\$0)

snippet bool
\tbool

snippet breakpoint
\tbreakpoint()

snippet bytearray
\tbytearray

snippet bytes
\tbytes

snippet callable
\tcallable(\$0)

snippet ce
\tce(\$0)

snippet chr
\tchr(\$0)

snippet classmethod
\tclassmethod

snippet complex
\tcomplex

snippet comprehension
\tcomprehension(\$0)

snippet copyright
\tcopyright()

snippet credits
\tcredits()

snippet decrement
\tdecrement(\$0)

snippet delattr
\tdelattr(\$0)

snippet dict
\tdict

snippet dir
\tdir(\$0)

snippet divmod
\tdivmod(\$0)

snippet enumerate
\tenumerate(\$0)

snippet eval
\teval(\$0)

snippet exec
\texec(\$0)

snippet exit
\texit(\$0)

snippet filter
\tfilter(\$0)

snippet float
\tfloat

snippet format
\tformat(\$0)

snippet frozenset
\tfrozenset

snippet frozendict
\tfrozendict

snippet getattr
\tgetattr(\$0)

snippet globals
\tglobals()

snippet hasattr
\thasattr(\$0)

snippet hash
\thash(\$0)

snippet help
\thelp(\$0)

snippet hex
\thex(\$0)

snippet id
\tid(\$0)

snippet increment
\tincrement(\$0)

snippet inf
\tinf

snippet infj
\tinfj

snippet input
\tinput(\$0)

snippet int
\tint

snippet isinstance
\tisinstance(\$0)

snippet isobjectof
\tisobjectof(\$0)

snippet issubclass
\tissubclass(\$0)

snippet iter
\titer(\$0)

snippet len
\tlen(\$0)

snippet license
\tlicense()

snippet list
\tlist(\$0)

snippet locals
\tlocals()

snippet map
\tmap(\$0)

snippet max
\tmax(\$0)

snippet memoryview
\tmemoryview

snippet min
\tmin(\$0)

snippet nce
\tnce(\$0)

snippet next
\tnext(\$0)

snippet nan
\tnan

snippet nanj
\tnanj

snippet object
\tobject

snippet oct
\toct(\$0)

snippet open
\topen(\$0)

snippet ord
\tord(\$0)

snippet pow
\tpow(\$0)

snippet print
\tprint(\$0)

snippet property
\tproperty

snippet pyimport
\tpyimport(\$0)

snippet quit
\tquit(\$0)

snippet range
\trange(\$0)

snippet repr
\trepr(\$0)

snippet require
\trequire(\$0)

snippet reversed
\treversed(\$0)

snippet round
\tround(\$0)

snippet set
\tset

snippet setattr
\tsetattr(\$0)

snippet slice
\tslice

snippet sorted
\tsorted(\$0)

snippet staticmethod
\tstaticmethod

snippet str
\tstr

snippet sum
\tsum(\$0)

snippet super
\tsuper(\$0)

snippet tuple
\ttuple

snippet type
\ttype

snippet unpack
\tunpack(\$0)

snippet vars
\tvars(\$0)

snippet zip
\tzip(\$0)

snippet fl
\tfor (i of range(\$1)) {
\t\t\$0
\t}

snippet fe
\tfor (item of \${1:iterableObject}) {
\t\t\$0
\t}

snippet lambda
\tfunc(\${1:parameter}) => \${0:returnValue}

snippet future
\tfrom __future__ import \${0:futureName}
`;