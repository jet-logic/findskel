from argparse import SUPPRESS
from os import DirEntry
from os import scandir, rmdir, unlink
from pathlib import Path
from sys import stderr
from .walkdir import FileSystemEntry
from .scantree import ScanTree


def filesizep(s: str):
    if s[0].isnumeric():
        for i, v in enumerate("bkmgtpezy"):
            if s[-1].lower().endswith(v):
                return int(s[0:-1]) * (2 ** (10 * i))
    return float(s)


def sizerangep(s=""):
    f, _, t = s.partition("..")
    a, b = [filesizep(f) if f else 0, filesizep(t) if t else float("inf")]
    return lambda n: n >= a and n <= b


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
