from os import DirEntry
from pathlib import Path
from .walkdir import FileSystemEntry
from . import FindSkel


class ListDir(FindSkel):

    def __init__(self) -> None:
        super().__init__()
        self._file_sizes = []
        self._dir_depth = ()
        self._glob_excludes = []
        self._glob_includes = []
        self._paths_from = []

    def add_arguments(self, argp):
        self.abs_path = True

        if not argp.description:
            argp.description = "List files under directory"

        return super().add_arguments(argp)

    def ready(self) -> None:

        return super().ready()

    def start(self):
        self._walk_paths()

    def process_entry(self, de: "DirEntry | FileSystemEntry") -> None:
        if self.abs_path:
            print((Path(self._root_dir) / de.path).absolute())
        else:
            super().process_entry(de)


# glob*
# type?
# time
# size*
# symlink check
# depth*
# --paths-from-lines
# --enter-symlinks=follow|no|top
# --follow-symlinks

(__name__ == "__main__") and ListDir().main()
