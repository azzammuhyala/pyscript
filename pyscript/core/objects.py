from .bases import Pys

class PysObject(Pys):
    pass

class PysCode(PysObject):

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PysModule(PysObject):

    def __init__(self, name, doc=None):
        self.__name__ = name
        self.__doc__ = doc

    def __dir__(self):
        return list(self.__dict__.keys())

    def __repr__(self):
        from .singletons import undefined

        file = self.__dict__.get('__file__', undefined)

        return '<module {!r}{}>'.format(
            self.__name__,
            '' if file is undefined else ' from {!r}'.format(file)
        )

    def __getattr__(self, name):
        raise AttributeError('module {!r} has no attribute {!r}'.format(self.__name__, name))

    def __delattr__(self, name):
        if name in self.__dict__:
            return super().__delattr__(name)
        raise AttributeError('module {!r} has no attribute {!r}'.format(self.__name__, name))

class PysPythonFunction(PysObject):

    def __init__(self, func):
        from .handlers import handle_call

        self.__name__ = func.__name__
        self.__qualname__ = func.__qualname__
        self.__func__ = func
        self.__code__ = PysCode(
            position=None,
            context=None,

            handle_call=handle_call
        )

    def __repr__(self):
        return '<python function {}>'.format(self.__name__)

    def __call__(self, *args, **kwargs):
        func = self.__func__
        code = self.__code__

        code.handle_call(func, code.context, code.position)
        return func(self, *args, **kwargs)

class PysFunction(PysObject):

    def __init__(self, name, qualname, parameters, body, position, context):
        from .context import PysContext
        from .exceptions import PysException, PysShouldReturn
        from .interpreter import interpreter
        from .results import PysRunTimeResult
        from .symtab import PysSymbolTable
        from .utils import join_with_conjunction, get_closest

        from types import MethodType

        self.__name__ = '<function>' if name is None else name
        self.__qualname__ = ('' if qualname is None else qualname + '.') + self.__name__
        self.__code__ = PysCode(
            parameters=parameters,
            body=body,
            position=position,
            context=context,

            PysContext=PysContext,
            PysException=PysException,
            PysShouldReturn=PysShouldReturn,
            PysRunTimeResult=PysRunTimeResult,
            PysSymbolTable=PysSymbolTable,
            join_with_conjunction=join_with_conjunction,
            get_closest=get_closest,
            MethodType=MethodType,

            interpreter=interpreter,
            call_context=context,
            argument_names=tuple(item for item in parameters if not isinstance(item, tuple)),
            keyword_argument_names=tuple(item[0] for item in parameters if isinstance(item, tuple)),
            parameter_names=tuple(item[0] if isinstance(item, tuple) else item for item in parameters),
            keyword_arguments={item[0]: item[1] for item in parameters if isinstance(item, tuple)}
        )

    def __repr__(self):
        return '<function {} at 0x{:016X}>'.format(self.__qualname__, id(self))

    def __get__(self, instance, owner):
        return self if instance is None else self.__code__.MethodType(self, instance)

    def __call__(self, *args, **kwargs):
        qualname = self.__qualname__
        code = self.__code__
        code_position = code.position
        code_context = code.context
        code_call_context = code.call_context
        code_parameter_names = code.parameter_names
        total_arguments = len(args)
        total_parameters = len(code.parameters)

        result = code.PysRunTimeResult()

        context = code.PysContext(
            file=code_context.file,
            name=self.__name__,
            qualname=qualname,
            symbol_table=code.PysSymbolTable(code_context.symbol_table),
            parent=code_call_context,
            parent_entry_position=code_position
        )

        registered_arguments = set()

        add_argument = registered_arguments.add
        set_symbol = context.symbol_table.set

        for name, arg in zip(code.argument_names, args):
            set_symbol(name, arg)
            add_argument(name)

        combined_keyword_arguments = code.keyword_arguments | kwargs

        pop_keyword_arguments = combined_keyword_arguments.pop

        for name, arg in zip(code.keyword_argument_names, args[len(registered_arguments):]):
            set_symbol(name, arg)
            add_argument(name)
            pop_keyword_arguments(name, None)

        for name, value in combined_keyword_arguments.items():

            if name in registered_arguments:
                raise code.PysShouldReturn(
                    result.failure(
                        code.PysException(
                            TypeError("{}() got multiple values for argument {!r}".format(qualname, name)),
                            code_call_context,
                            code_position
                        )
                    )
                )

            elif name not in code_parameter_names:
                closest_argument = code.get_closest(code_parameter_names, name)

                raise code.PysShouldReturn(
                    result.failure(
                        code.PysException(
                            TypeError(
                                "{}() got an unexpected keyword argument {!r}{}".format(
                                    qualname,
                                    name,
                                    '' if closest_argument is None else ". Did you mean {!r}?".format(closest_argument)
                                )
                            ),
                            code_call_context,
                            code_position
                        )
                    )
                )

            set_symbol(name, value)
            add_argument(name)

        total_registered = len(registered_arguments)

        if total_registered < total_parameters:
            missing_arguments = [name for name in code_parameter_names if name not in registered_arguments]
            total_missing = len(missing_arguments)

            raise code.PysShouldReturn(
                result.failure(
                    code.PysException(
                        TypeError(
                            "{}() missing {} required positional argument{}: {}".format(
                                qualname,
                                total_missing,
                                '' if total_missing == 1 else 's',
                                code.join_with_conjunction(missing_arguments, func=repr, conjunction='and')
                            )
                        ),
                        code_call_context,
                        code_position
                    )
                )
            )

        elif total_registered > total_parameters or total_arguments > total_parameters:
            given_arguments = total_arguments if total_arguments > total_parameters else total_registered

            raise code.PysShouldReturn(
                result.failure(
                    code.PysException(
                        TypeError(
                            "{}() takes no arguments ({} given)".format(qualname, given_arguments)
                            if total_parameters == 0 else
                            "{}() takes {} positional argument{} but {} were given".format(
                                qualname,
                                total_parameters,
                                '' if total_parameters == 1 else 's',
                                given_arguments
                            )
                        ),
                        code_call_context,
                        code_position
                    )
                )
            )

        result.register(code.interpreter.visit(code.body, context))
        if result.should_return() and not result.func_should_return:
            raise code.PysShouldReturn(result)

        return_value = result.func_return_value

        result.func_should_return = False
        result.func_return_value = None

        return return_value