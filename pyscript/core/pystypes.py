from .bases import Pys
from .context import PysContext, PysClassContext
from .exceptions import PysTraceback, PysSignal
from .nodes import PysNode
from .position import PysPosition
from .results import PysRunTimeResult
from .symtab import PysSymbolTable
from .utils.similarity import get_closest
from .utils.string import join

from types import MethodType
from typing import Any, Callable, Union

class PysObject(Pys):
    __slots__ = ()

class PysCode(PysObject):

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PysFunction(PysObject):

    def __init__(
        self,
        name: str | None,
        qualname: str | None,
        parameters: list[str | tuple[str, Any]],
        body: PysNode,
        context: PysContext,
        position: PysPosition
    ) -> None:

        # circular import problem solved
        from .interpreter import get_visitor

        context = context.parent if isinstance(context, PysClassContext) else context

        argument_names = []
        keyword_argument_names = []
        parameter_names = []
        keyword_arguments = {}

        append_argnames = argument_names.append
        append_keynames = keyword_argument_names.append
        append_paramnames = parameter_names.append
        set_keywordarg = keyword_arguments.__setitem__

        for parameter in parameters:
            if parameter.__class__ is tuple:
                arg, value = parameter
                append_paramnames(arg)
                append_keynames(arg)
                set_keywordarg(arg, value)
            else:
                append_paramnames(parameter)
                append_argnames(parameter)

        self.__name__ = name = '<function>' if name is None else name
        self.__qualname__ = name if qualname is None else f'{qualname}.{name}'
        self.__module__ = 'pyscript'
        self.__code__ = PysCode(
            parameters=tuple(parameters),
            body=body,
            context=context,
            position=position,
            file=context.file,
            closure_symbol_table=context.symbol_table,
            get_visitor=get_visitor,
            parameters_length=len(parameters),
            argument_names=tuple(argument_names),
            keyword_argument_names=tuple(keyword_argument_names),
            parameter_names=tuple(parameter_names),
            combine_keyword_arguments=keyword_arguments.__or__
        )

    def __repr__(self) -> str:
        return f'<function {self.__qualname__} at 0x{id(self):016X}>'

    def __get__(self, instance: Any | None, owner: type) -> Union['PysFunction', MethodType]:
        return self if instance is None else MethodType(self, instance)

    def __call__(self, *args, **kwargs) -> Any:
        code = self.__code__

        result = PysRunTimeResult()
        symbol_table = PysSymbolTable(code.closure_symbol_table)
        registered_arguments = set()

        set_symbol = symbol_table.set
        add_argument = registered_arguments.add

        for name, arg in zip(code.argument_names, args):
            set_symbol(name, arg)
            add_argument(name)

        combined_keyword_arguments = code.combine_keyword_arguments(kwargs)
        pop_keyword_arguments = combined_keyword_arguments.pop

        for name, arg in zip(code.keyword_argument_names, args[len(registered_arguments):]):
            set_symbol(name, arg)
            add_argument(name)
            pop_keyword_arguments(name, None)

        code_parameter_names = code.parameter_names

        for name, value in combined_keyword_arguments.items():

            if name in registered_arguments:
                raise PysSignal(
                    result.failure(
                        PysTraceback(
                            TypeError(f"{self.__qualname__}() got multiple values for argument {name!r}"),
                            code.context,
                            code.position
                        )
                    )
                )

            elif name not in code_parameter_names:
                closest_argument = get_closest(set(code_parameter_names), name)
                hint_message = "" if closest_argument is None else f". Did you mean {closest_argument!r}?"

                raise PysSignal(
                    result.failure(
                        PysTraceback(
                            TypeError(
                                f"{self.__qualname__}() got an unexpected keyword argument {name!r}{hint_message}"
                            ),
                            code.context,
                            code.position
                        )
                    )
                )

            set_symbol(name, value)
            add_argument(name)

        code_parameters_length = code.parameters_length
        arguments_length = len(args)
        total_registered = len(registered_arguments)

        if total_registered < code_parameters_length:
            missing_arguments = [repr(name) for name in code_parameter_names if name not in registered_arguments]
            total_missing = len(missing_arguments)

            raise PysSignal(
                result.failure(
                    PysTraceback(
                        TypeError(
                            f"{self.__qualname__}() missing {total_missing} required positional argument"
                            f"{'' if total_missing == 1 else 's'}: {join(missing_arguments, conjunction='and')}"
                        ),
                        code.context,
                        code.position
                    )
                )
            )

        elif total_registered > code_parameters_length or \
            (arguments_exceeding := arguments_length > code_parameters_length):
            given_arguments = arguments_length if arguments_exceeding else total_registered

            raise PysSignal(
                result.failure(
                    PysTraceback(
                        TypeError(
                            f"{self.__qualname__}() takes no arguments ({given_arguments} given)"
                            if code_parameters_length == 0 else
                            f"{self.__qualname__}() takes {code_parameters_length} positional argument"
                            f"{'' if code_parameters_length == 1 else 's'} but {given_arguments} were given"
                        ),
                        code.context,
                        code.position
                    )
                )
            )

        code_body = code.body

        result.register(
            code.get_visitor(code_body.__class__)(
                code_body,
                PysContext(
                    file=code.file,
                    name=self.__name__,
                    qualname=self.__qualname__,
                    symbol_table=symbol_table,
                    parent=code.context,
                    parent_entry_position=code.position
                )
            )
        )

        if result.should_return():
            if result.func_should_return:
                return result.func_return_value
            raise PysSignal(result)

class PysPythonFunction(PysFunction):

    def __init__(self, func: Callable) -> None:
        # circular import problem solved
        from .handlers import handle_call

        self.__func__ = func
        self.__name__ = getattr(func, '__name__', '<function>')
        self.__qualname__ = getattr(func, '__qualname__', '<function>')
        self.__module__ = getattr(func, '__module__', 'pyscript')
        self.__doc__ = getattr(func, '__doc__', None)
        self.__code__ = PysCode(
            context=None,
            position=None,
            handle_call=handle_call
        )

    def __repr__(self) -> str:
        return f'<python function {self.__qualname__} at 0x{id(self):016X}>'

    def __call__(self, *args, **kwargs) -> Any:
        func = self.__func__
        code = self.__code__
        code.handle_call(func, code.context, code.position)
        return func(self, *args, **kwargs)

class PysBuiltinFunction(PysPythonFunction):

    def __repr__(self) -> str:
        return f'<built-in function {self.__qualname__}>'
