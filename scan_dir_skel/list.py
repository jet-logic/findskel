from os import DirEntry
from pathlib import Path
from sys import stderr
from .walkdir import FileSystemEntry
from .scantree import ScanTree


class ListDir(ScanTree):

    def __init__(self) -> None:
        super().__init__()
        self._file_sizes = []
        self._dir_depth = ()

    def add_arguments(self, argp):
        self.bottom_up = True
        self.abs_path = True

        self._depth = None
        if not argp.description:
            argp.description = "List files under directory"

        return super().add_arguments(argp)

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
# --paths-from-lines
# --enter-symlinks=follow|no|top
# --follow-symlinks
