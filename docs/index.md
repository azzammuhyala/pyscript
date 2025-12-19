# PyScript Documention
> Note: This documentation is still empty or incomplete

PyScript is a simple programming language built on top of Python. It combines some syntax from Python and JavaScript,
so if you're already familiar with Python or JavaScript, or both, it should be quite easy to learn.

## Installation
First, you'll need to download Python. Make sure you're using the latest version above `3.10`, to ensure the code runs
correctly. Visit the official [Python website](https://python.org) to download it.

Next, after downloading and configuring the Python application, you can download the PyScript interpreter from
[PyScript releases](https://github.com/azzammuhyala/pyscript/releases) or from Python Pip with this command
(_Recommended_):
```sh
python -m pip install -U pyscript-programming-language
```

After that, you can run the PyScript shell (_REPL_) with this command:
```sh
python -m pyscript
```
If successful, you can see the version, release date, and a `>>>` like Python shell (_REPL_).

> If you are using the VS Code editor, you can use the
[PyScript extension](https://marketplace.visualstudio.com/items?itemName=azzammuhyala.pyslang) for Syntax Highlight!

## Repository
You can see the source code from [GitHub here](https://github.com/azzammuhyala/pyscript).

## Table of contents

- [PyScript Syntaxes](syntaxes/index.md)

    - Expressions

        - [Atom](syntaxes/expressions/atom.md)
        - [tuple](syntaxes/expressions/tuple.md)
        - [list](syntaxes/expressions/list.md)
        - [dict](syntaxes/expressions/dict.md)
        - [set](syntaxes/expressions/set.md)
        - [Primary](syntaxes/expressions/primary.md)
        - [Incremental](syntaxes/expressions/incremental.md)
        - [Power](syntaxes/expressions/power.md)
        - [Factor](syntaxes/expressions/factor.md)
        - [Term](syntaxes/expressions/term.md)
        - [Arith](syntaxes/expressions/arith.md)
        - [Bitwise](syntaxes/expressions/bitwise.md)
        - [Comp](syntaxes/expressions/comp.md)
        - [Member](syntaxes/expressions/member.md)
        - [Logic](syntaxes/expressions/logic.md)
        - [Nullish](syntaxes/expressions/nullish.md)
        - [Ternary](syntaxes/expressions/ternary.md)
        - [func / function](syntaxes/expressions/func.md)
        - [Walrus](syntaxes/expressions/walrus.md)

    - Statements

        - [from-import-as](syntaxes/statements/from-import-as.md)
        - [if-elif-else](syntaxes/statements/if-elif-else.md)
        - [switch-case-default](syntaxes/statements/switch-case-default.md)
        - [try-catch-else-finally](syntaxes/statements/try-catch-else-finally.md)
        - [with-as](syntaxes/statements/with-as.md)
        - [for-else](syntaxes/statements/for-else.md)
        - [while-else](syntaxes/statements/while-else.md)
        - [do-while-else](syntaxes/statements/do-while-else.md)
        - [class-extends](syntaxes/statements/class-extends.md)
        - [return](syntaxes/statements/return.md)
        - [global](syntaxes/statements/global.md)
        - [del / delete](syntaxes/statements/del.md)
        - [throw-from](syntaxes/statements/throw-from.md)
        - [assert](syntaxes/statements/assert.md)

- [PyScript Builtins](builtins/index.md)

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
    - [comprehension](builtins/builtins/comprehension.md)

- [PyScript Packages](packages/index.md)

    - PyScript Library

        - [ast](packages/pyscript-library/ast.md)
        - [tokenize](packages/pyscript-library/tokenize.md)
        - [ansi](packages/pyscript-library/ansi.md)
        - [brainfuck](packages/pyscript-library/brainfuck.md)
        - [explorer](packages/pyscript-library/explorer.md)
        - [fpstimer](packages/pyscript-library/fpstimer.md)
        - [getch](packages/pyscript-library/getch.md)
        - [inspect](packages/pyscript-library/inspect.md)
        - [jsdict](packages/pyscript-library/jsdict.md)
        - [keyword](packages/pyscript-library/keyword.md)
        - [parser](packages/pyscript-library/parser.md)
        - [site](packages/pyscript-library/site.md)
        - [symtab](packages/pyscript-library/symtable.md)
        - [sys](packages/pyscript-library/sys.md)
        - [token](packages/pyscript-library/token.md)

    - PyScript Python Packages

        - [Constants](packages/pyscript-python-packages/constants.md)

        - Functions

            - [pys_highlight](packages/pyscript-python-packages/functions/pys_highlight.md)
            - [pys_exec](packages/pyscript-python-packages/functions/pys_exec.md)
            - [pys_eval](packages/pyscript-python-packages/functions/pys_eval.md)
            - [pys_require](packages/pyscript-python-packages/functions/pys_require.md)
            - [pys_shell](packages/pyscript-python-packages/functions/pys_shell.md)

        - Classes

            - [PygmentsPyScriptLexer](packages/pyscript-python-packages/classes/pygments-pyscript-lexer.md)