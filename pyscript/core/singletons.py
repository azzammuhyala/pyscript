_singleton_objects = {}

class UndefinedType:

    __slots__ = ()

    def __new__(cls):
        if _singleton_objects.get('undefined', None) is None:
            _singleton_objects['undefined'] = super().__new__(cls)
        return _singleton_objects['undefined']

    def __bool__(self):
        return False

    def __repr__(self):
        return 'undefined'

undefined = UndefinedType()