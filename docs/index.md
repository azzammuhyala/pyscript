# PyScript Documention

> Note: This documentation is still empty or incomplete.

<div align="center">
    <img src="https://github.com/azzammuhyala/pyscript/blob/main/PyScript.png?raw=true" alt="PyScript Logo" width="200">
    <br>
    <a href="https://pepy.tech/project/pyscript-programming-language">
        <img src="https://static.pepy.tech/personalized-badge/pyscript-programming-language?period=total&units=NONE&left_color=GRAY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
    </a>
    <a href="https://en.wikipedia.org/wiki/MIT_License">
        <img src="https://img.shields.io/badge/license-MIT-orange" alt="MIT License">
    </a>
    <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.10+-yellow" alt="Python 3.10+">
    </a>
</div>

PyScript is a programming language built on top of Python. It combines some syntax from Python and JavaScript, so if
you're already familiar with Python, JavaScript or both, it should be quite easy to learn.

## Introduction 📖
The name of "PyScript" was previously used by a well-known framework designed to run Python directly in the browser.
Designed from the outset with inspiration from both Python and JavaScript, this language emphasizes human readability.
Its name was derived by combining **Py**thon and Java**Script**. Please note that this language is an independent
programming language project written in Python and has no affiliation with the aforementioned PyScript framework.

This language wasn't designed to compete with other modern programming languages, but rather as a learning for
understanding how programming languages ​​work and how human written code can be understood by machines. Furthermore, this
language was created as a relatively complex project. Using Python as the foundation for PyScript, it's easy to
understand how the language is built without having to understand complex instructions like those in C, C++, and other
low-level languages.

To learn more about PyScript, you can see on [PyScript documentation](https://azzammuhyala.github.io/pyscript) or 
[PyScript repository](https://github.com/azzammuhyala/pyscript) for full source code.

## Try PyScript ▶️
Try [PyScript Shell (_REPL_)](https://azzammuhyala.github.io/pyscript/shell.html) inside your browser directly
(no installation required).

## Installation ⬇️
First, you'll need to download Python. Make sure you're using the latest version above `3.10`, to ensure the code runs
correctly. Visit the official [Python website](https://python.org) to download it.

Next, after downloading and configuring the Python application, you can download the PyScript from
[PyScript releases](https://github.com/azzammuhyala/pyscript/releases) or from PIP with this command (_Recommended_):
```sh
pip install -U pyscript-programming-language
```

[_OPTIONAL_] You can download additional libraries that PyScript requires with this command:
```sh
pip install -U pyscript-programming-language[other]
```

And also, you can download PyScript with `git`:
```sh
git clone https://github.com/azzammuhyala/pyscript
cd pyscript
pip install .
```

After that, you can run the PyScript shell (_REPL_) with this command:
```sh
python -m pyscript
```
If successful, you can see the version, release date, and a `>>>` like Python shell (_REPL_).

## Library Requirements 📓
| No | Name              | Status                 |
|:--:|:------------------|:----------------------:|
| 1  | `argparse`        | **required**           |
| 2  | `builtins`        | **required**           |
| 3  | `cmath`           | **required**           |
| 4  | `collections.abc` | **required**           |
| 5  | `functools`       | **required**           |
| 6  | `html`            | **required**           |
| 7  | `importlib`       | **required**           |
| 8  | `inspect`         | **required**           |
| 9  | `io`              | **required**           |
| 10 | `itertools`       | **required**           |
| 11 | `json`            | **required**           |
| 12 | `operator`        | **required**           |
| 13 | `os`              | **required**           |
| 14 | `re`              | **required**           |
| 15 | `subprocess`      | **required**           |
| 16 | `sys`             | **required**           |
| 17 | `threading`       | **required**           |
| 18 | `types`           | **required**           |
| 19 | `typing`          | **required**           |
| 20 | `unicodedata`     | **required**           |
| 1  | `ast`             | **required (library)** |
| 2  | `msvcrt`          | **required (library)** |
| 3  | `pprint`          | **required (library)** |
| 4  | `shutil`          | **required (library)** |
| 5  | `stat`            | **required (library)** |
| 6  | `termios`         | **required (library)** |
| 7  | `time`            | **required (library)** |
| 8  | `tty`             | **required (library)** |
| 1  | `beartype`        | **optional**           |
| 2  | `prompt_toolkit`  | **optional**           |
| 3  | `pygments`        | **optional**           |
| 4  | `readline`        | **optional**           |
| 5  | `tkinter`         | **optional**           |
| 6  | `IPython`         | **optional**           |

### Status Explanation
- **required**: Required by PyScript entirely.
- **required (library)**: Required PyScript library (located in `pyscript/lib`). PyScript is not affected unless you
                          import it.
- **optional**: Not required, but if it is present, some features can be used without issue.

## Highlights 🎨
- [PyScript plugin for Acode (Ace Editor)](https://github.com/azzammuhyala/pyscript/releases/download/v1.13.3/plugin-1.0.2.zip)
- [PyScript nano for Linux](https://github.com/azzammuhyala/pyscript/tree/main/highlight/nano)
- [PyScript extension for VSCode](https://marketplace.visualstudio.com/items?itemName=azzammuhyala.pyslang)

## Behind It 🕰️
This language created from based up on a
[YouTube tutorial](https://www.youtube.com/playlist?list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD) (check more on GitHub
[here](https://github.com/davidcallanan/py-myopl-code) by **@davidcallanan**). At least, it takes about 6 months to
learn it, and also need to learn general things that exist in other programming languages.

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
        - [Primary](syntaxes/expressions/primary.md) [`<target>(<arguments>)`, `<target>[<slices>]`,
                                                      `<target>.<attribute>`]
        - [instanceof](syntaxes/expressions/instanceof.md) [`<object> instanceof <classes>`]
        - [Incremental](syntaxes/expressions/incremental.md) [`<target>++` / `++<target>`, `<target>--` / `--<target>`]
        - [Power](syntaxes/expressions/power.md) [`**`]
        - [Factor](syntaxes/expressions/factor.md) [`+<target>`, `-<target>`, `~<target>`]
        - [Term](syntaxes/expressions/term.md) [`*`, `/`, `//`, `%`, `@`]
        - [Arithmetic](syntaxes/expressions/arithmetic.md) [`+`, `-`]
        - [Bitwise](syntaxes/expressions/bitwise.md) [`&`, `|`, `^`, `<<`, `>>`]
        - [Comparison](syntaxes/expressions/comparison.md) [`not <target>` / `!<target>`, `==`, `!=` / `<>`, `~=`, `~!`,
                                                            `<`, `>`, `<=`, `>=`]
        - [Member](syntaxes/expressions/member.md) [`in` / `->`, `not in` / `!>`, `is`, `is not`]
        - [Logic](syntaxes/expressions/logic.md) [`and` / `&&`, `or` / `||`]
        - [Nullish](syntaxes/expressions/nullish.md) [`??`]
        - [Ternary](syntaxes/expressions/ternary.md) [`<condition> ? <valid> : <invalid>` /
                                                      `<valid> if <condition> else <invalid>`]
        - [typeof](syntaxes/expressions/typeof.md) [`typeof <target>`] (Lowest level operations)
        - [func/function - constructor](syntaxes/expressions/func-constructor.md) (Lowest level operations)
        - [match - default/else](syntaxes/expressions/match-default.md) (Lowest level operations)
        - [Walrus](syntaxes/expressions/walrus.md) [`:=`] (Lowest level operations)

    - Statements

        - [from - import - as](syntaxes/statements/from-import-as.md)
        - [if - elif/elseif/else if - else](syntaxes/statements/if-elif-else.md)
        - [switch - case - default/else](syntaxes/statements/switch-case-default.md)
        - [try - catch/except - else - finally](syntaxes/statements/try-catch-else-finally.md)
        - [with - as](syntaxes/statements/with-as.md)
        - [for - else](syntaxes/statements/for-else.md)
        - [while - else](syntaxes/statements/while-else.md)
        - [do - while - else](syntaxes/statements/do-while-else.md)
        - [repeat - until - else](syntaxes/statements/repeat-until-else.md)
        - [class - extends](syntaxes/statements/class-extends.md)
        - [return](syntaxes/statements/return.md)
        - [global](syntaxes/statements/global.md)
        - [del/delete](syntaxes/statements/del.md)
        - [throw/raise - from](syntaxes/statements/throw-from.md)
        - [assert](syntaxes/statements/assert.md)
        - [Decorator](syntaxes/statements/decorator.md)
        - [continue](syntaxes/statements/continue.md)
        - [break](syntaxes/statements/break.md)
        - [Assignment](syntaxes/statements/assignment.md)

- PyScript Builtins

    - [isobjectof](builtins/isobjectof.md)
    - [copyright](builtins/copyright.md)
    - [credits](builtins/credits.md)
    - [license](builtins/license.md)
    - [help](builtins/help.md)
    - [require](builtins/require.md)
    - [pyimport](builtins/pyimport.md)
    - [breakpoint](builtins/breakpoint.md)
    - [globals](builtins/globals.md)
    - [locals](builtins/locals.md)
    - [vars](builtins/vars.md)
    - [dir](builtins/dir.md)
    - [exec](builtins/exec.md)
    - [eval](builtins/eval.md)
    - [ce](builtins/ce.md)
    - [nce](builtins/nce.md)
    - [increment](builtins/increment.md)
    - [decrement](builtins/decrement.md)
    - [unpack](builtins/unpack.md)
    - [comprehension](builtins/comprehension.md)

- PyScript Packages

    - PyScript Library

        - [builtins](builtins/index.md)
        - [sys](packages/pyscript-library/sys.md)
        - [ast](packages/pyscript-library/ast.md)
        - [fpstimer](packages/pyscript-library/fpstimer.md)
        - [getch](packages/pyscript-library/getch.md)
        - [tokenize](packages/pyscript-library/tokenize.md)
        - [ansi](packages/pyscript-library/ansi.md)
        - [brainfuck](packages/pyscript-library/brainfuck.md)
        - [explorer](packages/pyscript-library/explorer.md)
        - [history](packages/pyscript-library/history.md)
        - [inspect](packages/pyscript-library/inspect.md)
        - [jsdict](packages/pyscript-library/jsdict.md)
        - [keyword](packages/pyscript-library/keyword.md)
        - [parser](packages/pyscript-library/parser.md)
        - [pdisplay](packages/pyscript-library/pdisplay.md)
        - [site](packages/pyscript-library/site.md)
        - [symtable](packages/pyscript-library/symtable.md)
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
            - [PygmentsPyScriptShellLexer](packages/pyscript-python-packages/classes/pygments-pyscript-shell-lexer.md)