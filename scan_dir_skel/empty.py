from os import DirEntry
from os import scandir, rmdir, unlink
from sys import stderr
from .walkdir import FileSystemEntry
from .scantree import ScanTree


class Empty(ScanTree):
    def __init__(self) -> None:
        super().__init__()
        self._file_sizes = []
        self._dir_depth = ()
        self._re_excludes = []
        self._re_includes = []

    def add_arguments(self, argp):
        self.bottom_up = True
        self.which = 0
        self.remove = False
        if not argp.description:
            argp.description = "List empty file or folder"
        group = argp.add_mutually_exclusive_group()
        group.add_argument("--files", action="store_const", help="files only", dest="which", const=1)
        group.add_argument("--dirs", action="store_const", help="folders only", dest="which", const=2)
        argp.add_argument("--remove", action="store_true", help="remove", dest="remove")

        def check(e: DirEntry, **kwargs):
            if e.is_file():
                return e.stat().st_size == 0
            elif e.is_dir():
                try:
                    it = scandir(e.path)
                except Exception as ex:
                    print("Error:", e.path, ex, file=stderr)
                else:
                    n = 0
                    with it:
                        try:
                            for _ in it:
                                n += 1
                                break
                            return n == 0
                        except Exception as ex:
                            print("Error:", e.path, ex, file=stderr)

        self.on_check_accept(check)
        return super().add_arguments(argp)

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:

        if de.is_file():
            if self.which not in (1, 0):
                return
            if self.remove:
                print("RM", de.path, file=stderr)
                unlink(de.path)
                return
        elif de.is_dir():
            if self.which not in (2, 0):
                return
            if self.remove:
                print("RD", de.path, file=stderr)
                rmdir(de.path)
                return
        else:
            return
        # if self.remove:
        #     if de.is_dir():
        #         print("RD", de.path, file=stderr)
        #         rmdir(de.path)
        #     else:
        #         print("RM", de.path, file=stderr)
        #         unlink(de.path)
        # else:
        print(de.path)


(__name__ == "__main__") and Empty().main()
