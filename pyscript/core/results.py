from .bases import Pys

class PysResult(Pys):
    __slots__ = ()

class PysParserResult(PysResult):

    def __init__(self):
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0
        self.fatal = False

        self.node = None
        self.error = None

    def register_advancement(self):
        self.last_registered_advance_count += 1
        self.advance_count += 1

    def register(self, result, require=False):
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        self.fatal = require or result.fatal

        self.error = result.error

        return result.node

    def try_register(self, result):
        if result.error and not result.fatal:
            self.to_reverse_count = result.advance_count
        else:
            return self.register(result)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error, fatal=True):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
            self.fatal = fatal
        return self

class PysRunTimeResult(PysResult):

    __slots__ = ('should_continue', 'should_break', 'func_return_value', 'func_should_return', 'value', 'error')

    def reset(self):
        self.should_continue = False
        self.should_break = False
        self.func_return_value = None
        self.func_should_return = False

        self.value = None
        self.error = None

    __init__ = reset

    def register(self, result):
        self.error = result.error

        self.should_continue = result.should_continue
        self.should_break = result.should_break
        self.func_return_value = result.func_return_value
        self.func_should_return = result.func_should_return

        return result.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        self.func_should_return = True
        return self

    def success_continue(self):
        self.reset()
        self.should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error or
            self.func_should_return or
            self.should_continue or
            self.should_break
        )

class PysExecuteResult(PysResult):

    def __init__(self, context):
        self.context = context

        self.value = None
        self.error = None

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self