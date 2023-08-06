import re
import shlex
from queue import Empty, Queue

import blessed
from fabric import Connection

T = blessed.Terminal()


# This is the implementation of shlex.join in Python >= 3.8
def shjoin(split_command):
    """Return a shell-escaped string from *split_command*."""
    return " ".join(shlex.quote(arg) for arg in split_command)


class QueueIO:
    def __init__(self):
        self.q = Queue()

    def write(self, s):
        self.q.put(s)

    def flush(self):
        pass

    def readlines(self, stop):
        current = ""
        while True:
            try:
                current += self.q.get(timeout=0.05)
                if "\n" in current:
                    *lines, current = current.split("\n")
                for line in lines:
                    yield f"{line}\n"
            except Empty:
                if stop():
                    if current:
                        yield current
                    return


class Remote:
    def __init__(self, host):
        self.host = host
        self.conn = Connection(host)

    def display(self, cmd):
        print(T.bold_cyan(f"({self.host}) $ ", cmd))

    def run(self, cmd, display=True, bash=False, **kwargs):
        if display:
            self.display(cmd)
        if bash:
            cmd = shjoin(["bash", "-c", cmd])
        return self.conn.run(cmd, **kwargs)

    def get(self, cmd, display=True, bash=False, **kwargs):
        return self.run(cmd, display=display, bash=bash, **kwargs).stdout.strip()

    def extract(self, cmd, pattern, wait=False, bash=False, **kwargs):
        kwargs.setdefault("pty", True)
        qio = QueueIO()
        proc = self.run(cmd, bash=bash, asynchronous=True, out_stream=qio, **kwargs)
        result = None
        try:
            for line in qio.readlines(lambda: proc.runner.process_is_finished):
                print(line, end="")
                m = re.search(pattern, line)
                if m:
                    result = m.groups()[0]
                    if not wait:
                        return proc.runner, result
        except KeyboardInterrupt:
            proc.runner.kill()
            raise
        proc.join()
        return proc.runner, result
