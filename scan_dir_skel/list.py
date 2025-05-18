from os import DirEntry
from pathlib import Path
from sys import stderr
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
        return (a, b)
    elif f:
        c = int(f)
        return (c, c)
    else:
        return (0, float("inf"))


class ListDir(ScanTree):
    _sizes: list[object]

    def __init__(self) -> None:
        super().__init__()
        self._sizes = []

    def add_arguments(self, argp):
        self.bottom_up = True
        self.abs_path = True
        self.includes = []

        self._depth = None
        if not argp.description:
            argp.description = "List files under directory"
        argp.add_argument(
            "--sizes",
            action="append",
            dest="_sizes",
            type=lambda x: sizerangep(x),
            help="Filter sizes",
        )
        argp.add_argument(
            "--depth",
            dest="_depth",
            type=lambda x: intrangep(x),
            help="Check for depth",
        )

        return super().add_arguments(argp)

    def ready(self) -> None:
        sizes = self._sizes
        if sizes:

            def check_size(de: DirEntry, **kwargs):
                ok = 0
                for f in sizes:
                    if f(de.stat().st_size):
                        ok += 1
                return ok > 0

            self.on_check_accept(check_size)
        depth: tuple[int, int] = self._depth
        if depth:
            a, b = depth

            # print("DEPTH", (a, b), file=stderr)

            def check_depth(de: DirEntry, **kwargs):
                d: int = kwargs["depth"]
                # print("check_depth", (d, (a, b)), de.path, file=stderr)
                return d >= a and d <= b

            def enter_depth(de: DirEntry, **kwargs):
                d: int = kwargs["depth"]
                # print("enter_depth", (d, b), de.path, file=stderr)
                return d <= b

            self.on_check_enter(enter_depth)
            self.on_check_accept(check_depth)
        return super().ready()

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        if self.abs_path:
            print((Path(self._root_dir) / de.path).absolute())
        else:
            super().process_entry(de)


(__name__ == "__main__") and ListDir().main()

# glob*
# type
# time
# size*
# symlink check
# depth*
