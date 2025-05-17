from os import scandir, rmdir, unlink


def dir_entry(entry, ctx):
    path = entry.path
    if entry.is_file():
        if entry.stat().st_size == 0:
            print(path)
    elif entry.is_dir():
        with scandir(path) as it:
            for entry in it:
                return
        print(path)


from . import ScanTree
from sys import stderr
from pathlib import Path


class ScanDir(ScanTree):

    def add_arguments(self, argp):
        self.name_re = []
        self.bottom_up = True
        self.files = True
        self.dirs = True
        self.remove = False
        self.excludes = []
        if not argp.description:
            argp.description = "list empty file or folder"
        argp.add_argument(
            "--files", action="store_false", help="files only", dest="dirs"
        )
        argp.add_argument(
            "--dirs", action="store_false", help="folders only", dest="files"
        )
        argp.add_argument("--remove", action="store_true", help="remove", dest="remove")

        super(ScanDir, self).add_arguments(argp)

    def dir_entry(self, entry):
        path = entry.path
        if entry.is_file():
            try:
                st = entry.stat()
            except:
                print("Error:", path, file=stderr)
                return
            else:
                if st.st_size == 0:
                    self.on_entry(entry)
        elif entry.is_dir():
            try:
                it = scandir(path)
            except:
                print("Error:", path, file=stderr)
                return
            else:
                with it:
                    try:
                        for entry in it:
                            return
                    except:
                        return
                self.on_entry(entry)

    def on_entry(self, entry):
        if entry.is_file():
            if self.files is not True:
                return
        elif entry.is_dir():
            if self.dirs is not True:
                return
        if self.remove:
            if entry.is_dir():
                print("RD", entry.path, file=stderr)
                rmdir(entry.path)
            else:
                print("RM", entry.path, file=stderr)
                unlink(entry.path)
        else:
            print(entry.path)

    def start(self):
        return super().start()


(__name__ == "__main__") and ScanDir().main()
