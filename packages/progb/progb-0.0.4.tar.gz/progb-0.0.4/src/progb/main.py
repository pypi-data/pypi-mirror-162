from os import get_terminal_size, system, name
from sys import stdout, platform

class Bar():
    def refresh(self):
        final = f"[{self.current}/{self.total}]"
        percentage = str(round((self.current / self.total)*100, 1))
        data_start = (" "*self.indent) + f"{self.title}|"
        icon = "⟳"
        if self.status == 1:
            icon = "⚠"
        if self.status == 2:
            icon = "✓"
        data_final = f"| {icon} {percentage}% {final}"
        available = self.size - (len(data_start) + len(data_final))
        if float(percentage) < 100:
            fill = round(available * (self.current/self.total))
        else:
            fill = available
        empty = round(available - fill)
        inner = "█"*fill + " "*empty
        output = data_start + inner + data_final
        stdout.write(u"\u001b[1000D")
        stdout.flush()
        stdout.write(output)
        stdout.flush()
        
    def __init__(self, total, title="", current=0, indent=0):
        # Enables ansi escape characters in terminal
        if platform == 'win32':
            os.system("")
        # Set object attributes
        self.total = total
        self.title = title
        self.size = get_terminal_size().columns
        self.current = current
        self.indent = indent
        #Set status to 0 (loading)
        self.status = 0
        self.refresh()

    def cycle(self):
        self.current = self.current+1
        # Check status for icon
        if self.total == self.current:
            self.status = 2
        if self.total < self.current:
            self.status = 1
        self.refresh()

    def end(self):
        # Check if ended without finishing
        if self.total != self.current:
            self.status = 1
        self.refresh()
        print("")

