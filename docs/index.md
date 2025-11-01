# PyScript Documention
PyScript is a simple programming language built on top of Python. It combines some syntax from Python and JavaScript, so
if you're already familiar with Python or JavaScript, or both, it should be quite easy to learn.

## Installation
First, you'll need to download Python. Make sure you're using the latest version, above `3.5`, to ensure the code runs
correctly. Visit the official [Python website](https://python.org) to download it.

Next, after downloading and configuring the Python application, you can download the PyScript interpreter from
[PyScript Releases](https://github.com/azzammuhyala/pyscript/releases) or from Python Pip with the command
(_Recommended_):
```sh
python -m pip install -U pyscript-programming-language
```

Now you can run the PyScript shell (_REPL_) with the command:
```sh
python -m pyscript
```
If successful, you should see the version, release date, and a `>>>` like Python shell.

## Repository
You can see the source code from [GitHub here](https://github.com/azzammuhyala/pyscript).

## Table of contents

- [PyScript Syntax](syntax/index.md)

    - Expressions

        - [Atom](syntax/expressions/atom.md)
        - [tuple](syntax/expressions/tuple.md)
        - [list](syntax/expressions/list.md)
        - [dict](syntax/expressions/dict.md)
        - [set](syntax/expressions/set.md)
        - [Primary](syntax/expressions/primary.md)
        - [Incremental](syntax/expressions/incremental.md)
        - [Power](syntax/expressions/power.md)
        - [Factor](syntax/expressions/factor.md)
        - [Term](syntax/expressions/term.md)
        - [Arith](syntax/expressions/arith.md)
        - [Bitwise](syntax/expressions/bitwise.md)
        - [Comp](syntax/expressions/comp.md)
        - [Member](syntax/expressions/member.md)
        - [Logic](syntax/expressions/logic.md)
        - [Nullish](syntax/expressions/nullish.md)
        - [Ternary](syntax/expressions/ternary.md)
        - [func](syntax/expressions/func.md)

    - Statements

        - [from-import-as](syntax/statements/from-import-as.md)
        - [if-elif-else](syntax/statements/if-elif-else.md)
        - [switch-case-default](syntax/statements/switch-case-default.md)
        - [try-catch-else-finally](syntax/statements/try-catch-else-finally.md)
        - [with-as](syntax/statements/with-as.md)
        - [for-else](syntax/statements/for-else.md)
        - [while-else](syntax/statements/while-else.md)
        - [do-while-else](syntax/statements/do-while-else.md)
        - [class-extends](syntax/statements/class-extends.md)
        - [return](syntax/statements/return.md)
        - [global](syntax/statements/global.md)
        - [del](syntax/statements/del.md)
        - [throw](syntax/statements/throw.md)
        - [assert](syntax/statements/assert.md)
        - [decorator](syntax/statements/decorator.md)

- [PyScript Builtins](builtins/index.md)

    - [pyimport](builtins/builtins/pyimport.md)
    - [require](builtins/builtins/require.md)
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
    - [isobjectof](builtins/builtins/isobjectof.md)

- [PyScript Packages](packages/index.md)

    - PyScript Library

        - [brainfuck](packages/pyscript-library/brainfuck.md)
        - [clock](packages/pyscript-library/clock.md)
        - [getch](packages/pyscript-library/getch.md)
        - [jsdict](packages/pyscript-library/jsdict.md)
        - [parser](packages/pyscript-library/parser.md)
        - [sys](packages/pyscript-library/sys.md)

    - PyScript Python Packages

        - [Constants](packages/pyscript-python-packages/constants.md)

        - Functions

            - [pys_eval](packages/pyscript-python-packages/functions/pys_eval.md)
            - [pys_exec](packages/pyscript-python-packages/functions/pys_exec.md)
            - [pys_highlight](packages/pyscript-python-packages/functions/pys_highlight.md)