from .bases import Pys
from .context import PysContext
from .exceptions import PysException
from .utils import join_with_conjunction

class PysShouldReturn(Exception):

    def __init__(self, result):
        super().__init__()
        self.result = result

class PysValue(Pys):

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value

class Error:

    __slots__ = ('name', 'message')

    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __repr__(self):
        return 'Error({!r}, {!r})'.format(self.name, self.message)

class PysMethod(Pys):

    __slots__ = ('function', 'instance')

    def __init__(self, function, instance):
        self.function = function
        self.instance = instance

    def __repr__(self):
        return '<bound method {} of {!r}>'.format(self.function.name, self.instance)

    def __call__(self, *args, **kwds):
        return self.function(self.instance, *args, **kwds)

class PysFunction(Pys):

    __slots__ = ()

    def __init__(self, position, context, name, parameter, body):
        self.position = position
        self.context = context
        self.name = name or '<function>'
        self.paramter = parameter
        self.body = body

        self.arg_names = [item for item in parameter if not isinstance(item, tuple)]
        self.kwarg_names = [item[0] for item in parameter if isinstance(item, tuple)]

        self.kwargs = {item[0]: item[1] for item in parameter if isinstance(item, tuple)}

    def __repr__(self):
        return '<function {} at 0x{:016X}>'.format(self.name, id(self))

    def __get__(self, instance, owner):
        return self if instance is None else PysMethod(self, instance)

    def __call__(self, *args, **kwargs):
        from .interpreter import PysRunTimeResult, PysInterpreter
        from .symtab import SymbolTable

        result = PysRunTimeResult()

        context = PysContext(self.name, self.context.file, self.position, self.context)
        context.symbol_table = SymbolTable(self.context.symbol_table)

        registered_args = set()
        index = 0

        for name, arg in zip(self.arg_names, args):
            context.symbol_table.set(name, arg)
            registered_args.add(name)
            index += 1

        input_kwargs = self.kwargs | kwargs

        for name, arg in zip(self.kwarg_names, args[index:]):
            context.symbol_table.set(name, arg)
            registered_args.add(name)
            input_kwargs.pop(name, None)

        for name, value in input_kwargs.items():
            if name in registered_args:
                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError("{}() got multiple values for argument '{}'".format(self.name, name)),
                            self.position,
                            self.context
                        )
                    )
                )

            else:
                context.symbol_table.set(name, value)
                registered_args.add(name)

        if len(registered_args) < len(self.paramter):
            missing_args = list((set(self.arg_names) | set(self.kwargs.keys())) - registered_args)
            total_missing = len(missing_args)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() missing {} required positional argument{}: {}".format(
                                self.name,
                                total_missing,
                                '' if total_missing == 1 else 's',
                                join_with_conjunction(missing_args, repr)
                            )
                        ),
                        self.position,
                        self.context
                    )
                )
            )

        elif len(registered_args) > len(self.paramter) or len(args) > len(self.paramter):
            total_input_args = len(args)
            total_args = len(self.paramter)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() takes {} positional argument{} but {} were given".format(
                                self.name,
                                total_args,
                                '' if total_args == 1 else 's',
                                total_input_args if total_input_args > total_args else len(registered_args)
                            )
                        ),
                        self.position,
                        self.context
                    )
                )
            )

        else:
            interpreter = PysInterpreter()
            result.register(interpreter.visit(self.body, context))

            return_value = result.func_return_value

            if result.should_return() and return_value is None:
                raise PysShouldReturn(result)

            return return_value.value if isinstance(return_value, PysValue) else return_value