from os import DirEntry
from os import scandir, rmdir, unlink
from sys import stderr
from .walkdir import FileSystemEntry
from .scantree import ScanTree


class InsertLines(ScanTree):

    def add_arguments(self, argp):
        self.bottom_up = True
        self.files = True
        self.dirs = True
        self.remove = False
        if not argp.description:
            argp.description = "List empty file or folder"
        argp.add_argument(
            "--files", action="store_false", help="files only", dest="dirs"
        )
        argp.add_argument(
            "--dirs", action="store_false", help="folders only", dest="files"
        )
        argp.add_argument("--remove", action="store_true", help="remove", dest="remove")
        return super().add_arguments(argp)

    def check_accept(self, e: DirEntry) -> bool:
        if super().check_accept(e):
            if e.is_file():
                return e.stat().st_size == 0
            elif e.is_dir():
                try:
                    it = scandir(e.path)
                except Exception as ex:
                    print("Error:", e.path, file=stderr)
                else:
                    n = 0
                    with it:
                        try:
                            for _ in it:
                                n += 1
                                break
                            return n == 0
                        except Exception as ex:
                            print("Error:", e.path, file=stderr)
        return False

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:

        if de.is_file():
            if self.files is not True:
                return
        elif de.is_dir():
            if self.dirs is not True:
                return
        if self.remove:
            if de.is_dir():
                print("RD", de.path, file=stderr)
                rmdir(de.path)
            else:
                print("RM", de.path, file=stderr)
                unlink(de.path)
        else:
            print(de.path)


(__name__ == "__main__") and InsertLines().main()
