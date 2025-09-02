from .bases import Pys

class PysPositionRange(Pys):

    def __init__(self, start, end):
        self.start = start
        self.end = end