from .bases import Pys

class PysBuffer(Pys):
    pass

class PysFileBuffer(PysBuffer):

    def __init__(self, text, name='<string>'):
        self.text = text
        self.name = name