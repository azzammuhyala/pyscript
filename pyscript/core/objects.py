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

    def __repr__(self):
        from .singletons import undefined
        file = getattr(self, '__file__', undefined)
        return '<module {!r}{}>'.format(self.__name__, '' if file is undefined else ' from {!r}'.format(file))

    def __getattr__(self, name):
        raise AttributeError('module {!r} has no attribute {!r}'.format(self.__name__, name))

    def __delattr__(self, name):
        if name not in self.__dict__:
            raise AttributeError('module {!r} has no attribute {!r}'.format(self.__name__, name))
        return super().__delattr__(name)

class PysPythonFunction(PysObject):

    def __init__(self, func):
        from .constants import DEFAULT

        self.__name__ = func.__name__
        self.__qualname__ = func.__qualname__
        self.__func__ = func
        self.__code__ = PysCode(position=None, context=None, flags=DEFAULT)

    def __repr__(self):
        return '<python function {}>'.format(self.__name__)

    def __call__(self, *args, **kwargs):
        from .handlers import handle_call
        handle_call(self.__func__, self.__code__.context, self.__code__.position, self.__code__.flags)
        return self.__func__(self, *args, **kwargs)

class PysFunction(PysObject):

    def __init__(self, name, qualname, parameters, body, position, context):
        from .constants import DEFAULT

        self.__name__ = '<function>' if name is None else name
        self.__qualname__ = ('' if qualname is None else qualname + '.') + self.__name__
        self.__code__ = PysCode(
            parameters=parameters,
            body=body,
            position=position,
            context=context,

            call_context=context,
            flags=DEFAULT,

            argument_names=tuple(item for item in parameters if not isinstance(item, tuple)),
            keyword_argument_names=tuple(item[0] for item in parameters if isinstance(item, tuple)),
            names=tuple(item[0] if isinstance(item, tuple) else item for item in parameters),
            keyword_arguments={item[0]: item[1] for item in parameters if isinstance(item, tuple)}
        )

    def __repr__(self):
        return '<function {} at 0x{:016X}>'.format(self.__qualname__, id(self))

    def __get__(self, instance, owner):
        from types import MethodType
        return self if instance is None else MethodType(self, instance)

    def __call__(self, *args, **kwargs):
        from .context import PysContext
        from .exceptions import PysException, PysShouldReturn
        from .interpreter import PysInterpreter
        from .results import PysRunTimeResult
        from .symtab import PysSymbolTable
        from .utils import join_with_conjunction, get_closest

        result = PysRunTimeResult()

        context = PysContext(
            file=self.__code__.context.file,
            name=self.__name__,
            qualname=self.__qualname__,
            symbol_table=PysSymbolTable(self.__code__.context.symbol_table),
            parent=self.__code__.call_context,
            parent_entry_position=self.__code__.position
        )

        registered_arguments = set()

        for name, arg in zip(self.__code__.argument_names, args):
            context.symbol_table.set(name, arg)
            registered_arguments.add(name)

        combined_keyword_arguments = self.__code__.keyword_arguments | kwargs

        for name, arg in zip(self.__code__.keyword_argument_names, args[len(registered_arguments):]):
            context.symbol_table.set(name, arg)
            registered_arguments.add(name)
            combined_keyword_arguments.pop(name, None)

        for name, value in combined_keyword_arguments.items():

            if name in registered_arguments:
                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError("{}() got multiple values for argument {!r}".format(self.__qualname__, name)),
                            self.__code__.call_context,
                            self.__code__.position
                        )
                    )
                )

            elif name not in self.__code__.names:
                closest_argument = get_closest(self.__code__.names, name)

                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError(
                                "{}() got an unexpected keyword argument {!r}{}".format(
                                    self.__qualname__,
                                    name,
                                    '' if closest_argument is None else ". Did you mean {!r}?".format(closest_argument)
                                )
                            ),
                            self.__code__.call_context,
                            self.__code__.position
                        )
                    )
                )

            context.symbol_table.set(name, value)
            registered_arguments.add(name)

        if len(registered_arguments) < len(self.__code__.parameters):
            missing_arguments = [name for name in self.__code__.names if name not in registered_arguments]
            total_missing = len(missing_arguments)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() missing {} required positional argument{}: {}".format(
                                self.__qualname__,
                                total_missing,
                                '' if total_missing == 1 else 's',
                                join_with_conjunction(missing_arguments, func=repr, conjunction='and')
                            )
                        ),
                        self.__code__.call_context,
                        self.__code__.position
                    )
                )
            )

        elif len(registered_arguments) > len(self.__code__.parameters) or len(args) > len(self.__code__.parameters):
            total_arguments = len(args)
            total_parameters = len(self.__code__.parameters)
            given_arguments = total_arguments if total_arguments > total_parameters else len(registered_arguments)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() takes no arguments ({} given)".format(self.__qualname__, given_arguments)
                            if total_parameters == 0 else
                            "{}() takes {} positional argument{} but {} were given".format(
                                self.__qualname__,
                                total_parameters,
                                '' if total_parameters == 1 else 's',
                                given_arguments
                            )
                        ),
                        self.__code__.call_context,
                        self.__code__.position
                    )
                )
            )

        interpreter = PysInterpreter(self.__code__.flags)

        result.register(interpreter.visit(self.__code__.body, context))
        if result.should_return() and not result.func_should_return:
            raise PysShouldReturn(result)

        return_value = result.func_return_value

        result.func_should_return = False
        result.func_return_value = None

        return return_value