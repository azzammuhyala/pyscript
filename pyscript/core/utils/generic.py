from inspect import currentframe

delimuattr = object.__delattr__
setimuattr = object.__setattr__

def get_locals(deep=1):
    frame = currentframe()

    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1

    if frame:
        locals = frame.f_locals
        return locals if isinstance(locals, dict) else dict(locals)

    return {}

def is_object_of(obj, class_or_tuple):
    return (
        isinstance(obj, class_or_tuple) or
        (isinstance(obj, type) and issubclass(obj, class_or_tuple))
    )

def get_error_args(exception):
    if exception is None:
        return None, None, None

    pyexception = exception.exception
    return (
        (pyexception, None, exception)
        if isinstance(pyexception, type) else
        (type(pyexception), pyexception, exception)
    )