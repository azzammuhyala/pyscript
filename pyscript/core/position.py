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
        return self.file.text.count('\n', 0, self.start) + 1

    @property
    def end_line(self):
        return self.file.text.count('\n', 0, self.end) + 1

    @property
    def start_column(self):
        return self.start - self.file.text.rfind('\n', 0, self.start)

    @property
    def end_column(self):
        return self.end - self.file.text.rfind('\n', 0, self.end)

    def format_arrow(self):
        string = ''

        line_start = self.start_line
        column_start = self.start_column
        line_end = self.end_line
        column_end = self.end_column

        start = self.file.text.rfind('\n', 0, self.start) + 1
        end = self.file.text.find('\n', start + 1)
        if end == -1:
            end = len(self.file.text)

        if self.file.text[self.start:self.end] in {'', '\n'}:
            line = self.file.text[start:end].lstrip('\n')

            string += line + '\n'
            string += ' ' * len(line) + '^'

        else:
            lines = []
            count = line_end - line_start + 1

            for i in range(count):
                line = self.file.text[start:end].lstrip('\n')

                lines.append(
                    (
                        line, len(line.lstrip()),
                        column_start - 1 if i == 0 else 0, column_end - 1 if i == count - 1 else len(line)
                    )
                )

                start = end
                end = self.file.text.find('\n', start + 1)
                if end == -1:
                    end = len(self.file.text)

            removed_indent = min(len(line) - no_indent for line, no_indent, _, _ in lines)

            for i, (line, no_indent, start, end) in enumerate(lines):
                line = line[removed_indent:]
                string += line + '\n'

                if i == 0:
                    arrow = '^' * (end - start)
                    line_arrow = ' ' * (start - removed_indent) + arrow

                else:
                    indent = len(line) - no_indent
                    arrow = '^' * (end - start - (removed_indent + indent))
                    line_arrow = ' ' * indent + arrow

                if arrow and len(line_arrow) - 1 <= len(line):
                    string += line_arrow + '\n'

        return string.rstrip().replace('\t', ' ')