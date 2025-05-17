from os import DirEntry
from pathlib import Path
from .walkdir import FileSystemEntry
from .scantree import ScanTree


def filesizep(s: str):
    if s[0].isnumeric():
        q = s.lower().rstrip("b")
        for i, v in enumerate("kmgtpezy"):
            if q[-1].endswith(v):
                return float(q[0:-1]) * (2 ** (10 * (i + 1)))
        return float(q)
    return float(s)


def sizerangep(s=""):
    f, d, t = s.partition("..")
    if d:
        a, b = [filesizep(f) if f else 0, filesizep(t) if t else float("inf")]
        return lambda n: n >= a and n <= b
    elif f:
        c = filesizep(f)
        return lambda n: n == c
    else:
        return lambda n: n >= 0


def intrangep(s=""):
    f, d, t = s.partition("..")
    if d:
        a, b = [int(f) if f else 0, int(t) if t else float("inf")]
        return lambda n: n >= a and n <= b
    elif f:
        c = int(f)
        return lambda n: n == c
    else:
        return lambda n: n >= 0


class ListDir(ScanTree):

    def add_arguments(self, argp):
        self.bottom_up = True
        self.files = True
        self.dirs = True
        self.abs_path = True
        self._sizes = []
        if not argp.description:
            argp.description = "List files under directory"
        if 1:
            argp.add_argument(
                "--sizes",
                action="append",
                dest="_sizes",
                help="filter sizes",
            )

        return super().add_arguments(argp)

    def check_accept(self, e: DirEntry) -> bool:
        return super().check_accept(e)

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        if self.abs_path:
            print((Path(self._root_dir) / de.path).absolute())
        else:
            super().process_entry(de)


(__name__ == "__main__") and ListDir().main()
