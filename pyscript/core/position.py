from .bases import Pys

class PysPosition(Pys):

    def __init__(self, file, start, end):
        self.file = file
        self.start = start
        self.end = end

    def __repr__(self):
        return '<Position({!r}, {!r}) from {!r}>'.format(self.start, self.end, self.file.name)

    @property
    def start_line(self):
        return -1 if self.is_positionless() else self.file.text.count('\n', 0, self.start) + 1

    @property
    def start_column(self):
        return -1 if self.is_positionless() else self.start - self.file.text.rfind('\n', 0, self.start)

    @property
    def end_line(self):
        return -1 if self.is_positionless() else self.file.text.count('\n', 0, self.end) + 1

    @property
    def end_column(self):
        return -1 if self.is_positionless() else self.end - self.file.text.rfind('\n', 0, self.end)

    def is_positionless(self):
        start, end = self.start, self.end
        return start < 0 or end < 0 or start > end

    def format_arrow(self):
        if self.is_positionless():
            return ''

        line_start = self.start_line
        line_end = self.end_line
        column_start = self.start_column
        column_end = self.end_column

        text = self.file.text

        start = text.rfind('\n', 0, self.start) + 1
        end = text.find('\n', start + 1)
        if end == -1:
            end = len(text)

        if text[self.start:self.end] in {'', '\n'}:
            line = text[start:end].lstrip().replace('\t', ' ')
            return '{}\n{}^'.format(line, ' ' * len(line))

        result = []
        lines = []
        count = line_end - line_start + 1

        for i in range(count):
            line = text[start:end].lstrip('\n')

            lines.append(
                (
                    line,
                    len(line.lstrip()),
                    column_start - 1 if i == 0 else 0,
                    column_end - 1 if i == count - 1 else len(line)
                )
            )

            start = end
            end = text.find('\n', start + 1)
            if end == -1:
                end = len(text)

        removed_indent = min(len(line) - line_code_length for line, line_code_length, _, _ in lines)

        for i, (line, line_code_length, start, end) in enumerate(lines):
            line = line[removed_indent:]
            result.append(line)

            if i == 0:
                arrow = '^' * (end - start)
                line_arrow = ' ' * (start - removed_indent) + arrow

            else:
                indent = len(line) - line_code_length
                arrow = '^' * (end - start - (removed_indent + indent))
                line_arrow = ' ' * indent + arrow

            if arrow and len(line_arrow) - 1 <= len(line):
                result.append(line_arrow)

        return '\n'.join(result).replace('\t', ' ')