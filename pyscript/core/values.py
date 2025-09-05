from .bases import Pys
from .context import PysContext
from .exceptions import PysException
from .utils import join_with_conjunction

class PysShouldReturn(Exception):

    def __init__(self, result):
        super().__init__()
        self.result = result

class PysMethod(Pys):

    def __init__(self, function, instance):
        self.function = function
        self.instance = instance

    def __repr__(self):
        return '<bound method {} of {!r}>'.format(self.function.__name__, self.instance)

    def __call__(self, *args, **kwds):
        return self.function(self.instance, *args, **kwds)

class PysFunction(Pys):

    def __init__(self, name, parameter, body, position, context):
        self.__name__ = name or '<function>'

        self._paramter = parameter
        self._body = body
        self._position = position
        self._context = context

        self._arg_names = [item for item in parameter if not isinstance(item, tuple)]
        self._kwarg_names = [item[0] for item in parameter if isinstance(item, tuple)]

        self._kwargs = {item[0]: item[1] for item in parameter if isinstance(item, tuple)}

    def __repr__(self):
        return '<function {} at 0x{:016X}>'.format(self.__name__, id(self))

    def __get__(self, instance, owner):
        return self if instance is None else PysMethod(self, instance)

    def __call__(self, *args, **kwargs):
        from .interpreter import PysRunTimeResult, PysInterpreter
        from .symtab import PysSymbolTable

        result = PysRunTimeResult()

        context = PysContext(self.__name__, self._context.file, self._position, self._context)
        context.symbol_table = PysSymbolTable(self._context.symbol_table)

        registered_args = set()
        index = 0

        for name, arg in zip(self._arg_names, args):
            context.symbol_table.set(name, arg)
            registered_args.add(name)
            index += 1

        input_kwargs = self._kwargs | kwargs

        for name, arg in zip(self._kwarg_names, args[index:]):
            context.symbol_table.set(name, arg)
            registered_args.add(name)
            input_kwargs.pop(name, None)

        for name, value in input_kwargs.items():
            if name in registered_args:
                raise PysShouldReturn(
                    result.failure(
                        PysException(
                            TypeError("{}() got multiple values for argument '{}'".format(self.__name__, name)),
                            self._position,
                            self._context
                        )
                    )
                )

            else:
                context.symbol_table.set(name, value)
                registered_args.add(name)

        if len(registered_args) < len(self._paramter):
            missing_args = list((set(self._arg_names) | set(self._kwargs.keys())) - registered_args)
            total_missing = len(missing_args)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() missing {} required positional argument{}: {}".format(
                                self.__name__,
                                total_missing,
                                '' if total_missing == 1 else 's',
                                join_with_conjunction(missing_args, repr)
                            )
                        ),
                        self._position,
                        self._context
                    )
                )
            )

        elif len(registered_args) > len(self._paramter) or len(args) > len(self._paramter):
            total_input_args = len(args)
            total_args = len(self._paramter)

            raise PysShouldReturn(
                result.failure(
                    PysException(
                        TypeError(
                            "{}() takes {} positional argument{} but {} were given".format(
                                self.__name__,
                                total_args,
                                '' if total_args == 1 else 's',
                                total_input_args if total_input_args > total_args else len(registered_args)
                            )
                        ),
                        self._position,
                        self._context
                    )
                )
            )

        else:
            interpreter = PysInterpreter()
            result.register(interpreter.visit(self._body, context))

            if result.should_return() and result.func_return_value is None:
                raise PysShouldReturn(result)

            return result.func_return_value