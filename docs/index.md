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

        - [func](syntax/expressions/func.md)
        - [Ternary](syntax/expressions/ternary.md)
        - [Logic](syntax/expressions/logic.md)
        - [Member](syntax/expressions/member.md)
        - [Comp](syntax/expressions/comp.md)
        - [Bitwise](syntax/expressions/bitwise.md)
        - [Arith](syntax/expressions/arith.md)
        - [Term](syntax/expressions/term.md)
        - [Factor](syntax/expressions/factor.md)
        - [Power](syntax/expressions/power.md)
        - [Incremental](syntax/expressions/incremental.md)
        - [Nullish](syntax/expressions/nullish.md)
        - [Primary](syntax/expressions/primary.md)
        - [Atom](syntax/expressions/atom.md)
        - [tuple](syntax/expressions/tuple.md)
        - [list](syntax/expressions/list.md)
        - [dict](syntax/expressions/dict.md)
        - [set](syntax/expressions/set.md)

    - Statements

        - [from-import-as](syntax/statements/from-import-as.md)
        - [if-elif-else](syntax/statements/if-elif-else.md)
        - [switch-case-default](syntax/statements/switch-case-default.md)
        - [try-catch-else-finally](syntax/statements/try-catch-else-finally.md)
        - [for-else](syntax/statements/for-else.md)
        - [while-else](syntax/statements/while-else.md)
        - [do-while-else](syntax/statements/do-while-else.md)
        - [class](syntax/statements/class.md)
        - [return](syntax/statements/return.md)
        - [global](syntax/statements/global.md)
        - [del](syntax/statements/del.md)
        - [throw](syntax/statements/throw.md)
        - [assert](syntax/statements/assert.md)
        - [decorator](syntax/statements/decorator.md)

- [PyScript Builtins](builtins/index.md)

- [PyScript Packages](packages/index.md)