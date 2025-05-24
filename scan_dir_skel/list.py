from os import DirEntry
from pathlib import Path
import re
from sys import stderr
from .walkdir import FileSystemEntry
from .scantree import ScanTree


class ListDir(ScanTree):

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

        _glob_includes: list[str] = getattr(self, "_glob_includes", None)
        _glob_excludes: list[str] = getattr(self, "_glob_excludes", None)

        if _glob_excludes is not None or _glob_includes is not None:

            argp.add_argument(
                "--exclude",
                metavar="GLOB",
                action="append",
                # type=lambda s: globre3(s, escape=escape, no_neg=True),
                dest="_glob_excludes",
                help="exclude matching GLOB",
            )
            argp.add_argument(
                "--include",
                metavar="GLOB",
                action="append",
                # type=lambda s: globre3(s, escape=escape, no_neg=True),
                dest="_glob_includes",
                help="include matching GLOB",
            )
        return super().add_arguments(argp)

    def ready(self) -> None:
        _glob_includes: list[str] = getattr(self, "_glob_includes", None)
        _glob_excludes: list[str] = getattr(self, "_glob_excludes", None)
        # print("_glob_includes", _glob_includes, file=stderr)
        # print("_glob_excludes", _glob_excludes, file=stderr)
        if _glob_includes or _glob_excludes:
            from os.path import relpath, sep
            from re import compile as regex, escape

            def makef(s: str):
                (rex, dir_only, neg, g) = globre3(s, escape=escape, no_neg=True)
                m = regex(rex)

                def col(r="", is_dir=False):
                    return (is_dir if dir_only else True) and m.search(r)

                return col

            # globre3(s, escape=escape, no_neg=True),
            # tuple[bool, str, bool, str]
            inc = [makef(s) for s in _glob_includes]
            exc = [makef(s) for s in _glob_excludes]

            def check_glob(e: DirEntry, **kwargs):
                is_dir = e.is_dir()
                rel = relpath(e.path, self._root_dir)
                # print("check_glob", e, r, s)
                # if not any(m(rel, is_dir) for m in globs):
                #     return False
                if inc:
                    if not any(m(rel, is_dir) for m in inc):
                        return False
                if exc:
                    if any(m(rel, is_dir) for m in exc):
                        return False

            self.on_check_accept(check_glob)
        return super().ready()

    def start(self):
        self._walk_paths()

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        if self.abs_path:
            print((Path(self._root_dir) / de.path).absolute())
        else:
            super().process_entry(de)


def globre3(g: str, base="", escape=lambda x: "", no_neg=False):

    if no_neg is False and g.startswith("!"):
        neg = True
        g = g[1:]
    else:
        neg = None
    if g.endswith("/"):
        g = g[0:-1]
        dir_only = True
    else:
        dir_only = None
    i = g.find("/")
    if i < 0:
        at_start = False
    elif i == 0:
        at_start = True
        g = g[1:]
    else:
        at_start = None
    i, n = 0, len(g)
    res = ""
    while i < n:
        c = g[i]
        i = i + 1
        if c == "*":
            if i < n and "*" == g[i]:
                i = i + 1
                res = res + ".*"
                if i < n and "/" == g[i]:
                    i = i + 1
                    res += "/?"
            else:
                res = res + "[^/]+"
        elif c == "?":
            res = res + "[^/]"
        elif c == "[":
            j = i
            if j < n and g[j] == "!":
                j = j + 1
            if j < n and g[j] == "]":
                j = j + 1
            while j < n and g[j] != "]":
                j = j + 1
            if j >= n:
                res = res + "\\["
            else:
                stuff = g[i:j].replace("\\", "\\\\")
                i = j + 1
                if stuff[0] == "!":
                    stuff = "^" + stuff[1:]
                elif stuff[0] == "^":
                    stuff = "\\" + stuff
                res = "%s[%s]" % (res, stuff)
        else:
            res = res + escape(c)
    if at_start:
        if base:
            res = "^" + escape(base) + "/" + res + r"\Z"
        else:
            res = "^" + res + r"\Z"
    else:
        if base:
            res = r"(?ms)\A" + escape(base) + r"/(?:|.+/)" + res + r"\Z"
        else:
            res = r"(?:|.+/)" + res + r"\Z"
        assert at_start in (None, False)

    return (res, dir_only, neg, g)


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
