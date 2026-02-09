# PyScript Documention

<div align="center">
    <img src="https://github.com/azzammuhyala/pyscript/blob/main/PyScript.png?raw=true" alt="PyScript Logo" width="200">
</div>

> Note: This documentation is still empty or incomplete

PyScript is a simple programming language built on top of Python. It combines some syntax from Python and JavaScript,
so if you're already familiar with Python, JavaScript or both, it should be quite easy to learn.

## Introduction
PyScript may not be the language we'll be discussing, but the name PyScript already exists, a flexible and platform for
running Python in a browser. Since it's inception, the language was inspired by Python and JavaScript, which are
relatively easy for humans to read. This name was chosen because it wasn't immediately known whether this name was
already in use.

This language wasn't designed to compete with other modern programming languages, but rather as a learning for
understanding how programming languages ​​work and how human written code can be understood by machines. Furthermore, this
language was created as a relatively complex project. Using Python as the foundation for PyScript, it's easy to
understand how the language is built without having to understand complex instructions like those in C, C++, and other
low-level languages.

To learn more about PyScript, you can see on [PyScript documentation](https://azzammuhyala.github.io/pyscript) or 
[PyScript repository](https://github.com/azzammuhyala/pyscript) for full source code.

## Installation
First, you'll need to download Python. Make sure you're using the latest version above `3.10`, to ensure the code runs
correctly. Visit the official [Python website](https://python.org) to download it.

Next, after downloading and configuring the Python application, you can download the PyScript from
[PyScript releases](https://github.com/azzammuhyala/pyscript/releases) or from Python Pip with this command
(_Recommended_):
```sh
pip install -U pyscript-programming-language
```

[_OPTIONAL_] You can download additional libraries that PyScript requires with this command:
```sh
pip install -U "pyscript-programming-language[other]"
```

And also, you can download PyScript with `git`:
```sh
git clone https://github.com/azzammuhyala/pyscript
cd pyscript
python setup.py install
```

After that, you can run the PyScript shell (_REPL_) with this command:
```sh
python -m pyscript
```
If successful, you can see the version, release date, and a `>>>` like Python shell (_REPL_).

> If you are using the VS Code editor, you can use the
[PyScript extension](https://marketplace.visualstudio.com/items?itemName=azzammuhyala.pyslang) for Syntax Highlight!

## Table of contents

- [PyScript Syntaxes](syntaxes/index.md)

    - Expressions

        - [Atom](syntaxes/expressions/atom.md) [`__debug__`, `True` / `true`, `False` / `false`, `None` / `nil` / `none`
                                                / `null`, identifier, number, string, tuple, list, dict, set, `...`]
                                               (Highest level operations)
        - [tuple](syntaxes/expressions/tuple.md) [`(<elements>)`]
        - [list](syntaxes/expressions/list.md) [`[<elements>]`]
        - [dict](syntaxes/expressions/dict.md) [`{<key>: <value>}`]
        - [set](syntaxes/expressions/set.md) [`{<elements>}`]
        - [Primary](syntaxes/expressions/primary.md) [`<target>(<parameters>)`, `<target>[<indexes>]`,
                                                      `<target>.<attribute>`]
        - [Incremental](syntaxes/expressions/incremental.md) [`<target>++` / `++<target>`, `<target>--` / `--<target>`]
        - [Power](syntaxes/expressions/power.md) [`**`]
        - [Factor](syntaxes/expressions/factor.md) [`+<target>`, `-<target>`, `~<target>`]
        - [Term](syntaxes/expressions/term.md) [`*`, `/`, `//`, `%`, `@`]
        - [Arithmetic](syntaxes/expressions/arithmetic.md) [`+`, `-`]
        - [Bitwise](syntaxes/expressions/bitwise.md) [`&`, `|`, `^`, `<<`, `>>`]
        - [Comparison](syntaxes/expressions/comparison.md) [`not <target>` / `!<target>`, `==`, `!=`, `~=`, `~!`, `<`,
                                                            `>`, `<=`, `>=`]
        - [Member](syntaxes/expressions/member.md) [`in` / `->`, `not in` / `!>`, `is`, `is not`]
        - [Logic](syntaxes/expressions/logic.md) [`and` / `&&`, `or` / `||`]
        - [Nullish](syntaxes/expressions/nullish.md) [`??`]
        - [Ternary](syntaxes/expressions/ternary.md) [`<condition> ? <valid> : <invalid>` /
                                                      `<valid> if <condition> else <invalid>`]
        - [typeof](syntaxes/expressions/typeof.md) [`typeof <target>`] (Lowest level operations)
        - [def/define/func/function - constructor](syntaxes/expressions/func-constructor.md) (Lowest level operations)
        - [match-default](syntaxes/expressions/match-default.md) (Lowest level operations)
        - [Walrus](syntaxes/expressions/walrus.md) [`:=`] (Lowest level operations)

    - Statements

        - [Assignment](syntaxes/statements/assignment.md)
        - [from-import-as](syntaxes/statements/from-import-as.md)
        - [if - elif/elseif - else](syntaxes/statements/if-elif-else.md)
        - [switch-case-default](syntaxes/statements/switch-case-default.md)
        - [try-catch-else-finally](syntaxes/statements/try-catch-else-finally.md)
        - [with-as](syntaxes/statements/with-as.md)
        - [for-else](syntaxes/statements/for-else.md)
        - [while-else](syntaxes/statements/while-else.md)
        - [do-while-else](syntaxes/statements/do-while-else.md)
        - [repeat-until-else](syntaxes/statements/repeat-until-else.md)
        - [class-extends](syntaxes/statements/class-extends.md)
        - [return](syntaxes/statements/return.md)
        - [global](syntaxes/statements/global.md)
        - [del/delete](syntaxes/statements/del.md)
        - [raise/throw - from](syntaxes/statements/throw-from.md)
        - [assert](syntaxes/statements/assert.md)
        - [Decorator](syntaxes/statements/decorator.md)

- [PyScript Builtins](builtins/index.md)

    - [copyright](builtins/builtins/copyright.md)
    - [credits](builtins/builtins/credits.md)
    - [isobjectof](builtins/builtins/isobjectof.md)
    - [license](builtins/builtins/license.md)
    - [help](builtins/builtins/help.md)
    - [require](builtins/builtins/require.md)
    - [pyimport](builtins/builtins/pyimport.md)
    - [breakpoint](builtins/builtins/breakpoint.md)
    - [globals](builtins/builtins/globals.md)
    - [locals](builtins/builtins/locals.md)
    - [vars](builtins/builtins/vars.md)
    - [dir](builtins/builtins/dir.md)
    - [exec](builtins/builtins/exec.md)
    - [eval](builtins/builtins/eval.md)
    - [ce](builtins/builtins/ce.md)
    - [nce](builtins/builtins/nce.md)
    - [increment](builtins/builtins/increment.md)
    - [decrement](builtins/builtins/decrement.md)
    - [unpack](builtins/builtins/unpack.md)
    - [comprehension](builtins/builtins/comprehension.md)

- [PyScript Packages](packages/index.md)

    - PyScript Library

        - [ast](packages/pyscript-library/ast.md)
        - [fpstimer](packages/pyscript-library/fpstimer.md)
        - [tokenize](packages/pyscript-library/tokenize.md)
        - [ansi](packages/pyscript-library/ansi.md)
        - [brainfuck](packages/pyscript-library/brainfuck.md)
        - [explorer](packages/pyscript-library/explorer.md)
        - [getch](packages/pyscript-library/getch.md)
        - [inspect](packages/pyscript-library/inspect.md)
        - [jsdict](packages/pyscript-library/jsdict.md)
        - [keyword](packages/pyscript-library/keyword.md)
        - [parser](packages/pyscript-library/parser.md)
        - [site](packages/pyscript-library/site.md)
        - [symtable](packages/pyscript-library/symtable.md)
        - [sys](packages/pyscript-library/sys.md)
        - [token](packages/pyscript-library/token.md)

    - PyScript Python Packages

        - [Constants](packages/pyscript-python-packages/constants.md)

        - Functions

            - [pys_highlight](packages/pyscript-python-packages/functions/pys_highlight.md)
            - [pys_runner](packages/pyscript-python-packages/functions/pys_runner.md)
            - [pys_exec](packages/pyscript-python-packages/functions/pys_exec.md)
            - [pys_eval](packages/pyscript-python-packages/functions/pys_eval.md)
            - [pys_require](packages/pyscript-python-packages/functions/pys_require.md)
            - [pys_shell](packages/pyscript-python-packages/functions/pys_shell.md)

        - Classes

            - [PygmentsPyScriptStyle](packages/pyscript-python-packages/classes/pygments-pyscript-style.md)
            - [PygmentsPyScriptLexer](packages/pyscript-python-packages/classes/pygments-pyscript-lexer.md)