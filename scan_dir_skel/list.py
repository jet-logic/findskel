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
        self._re_excludes = []
        self._re_includes = []
        self._globs: list[tuple[bool, str, bool, str]] = []

    def add_arguments(self, argp):
        # self.bottom_up = True
        self.abs_path = True

        if not argp.description:
            argp.description = "List files under directory"
        from re import escape

        argp.add_argument(
            "--glob",
            metavar="GLOB",
            action="append",
            type=lambda s: globre3(s, "", escape),
            dest="_globs",
            help="matching GLOB",
        )
        return super().add_arguments(argp)

    def ready(self) -> None:
        print("bottom_up", self.bottom_up, file=stderr)
        print("_globs", self._globs, file=stderr)
        if self._globs:
            from os.path import relpath, sep

            def makef(m, dir_only, neg):
                def col(r="", is_dir=False):
                    return (is_dir if dir_only else True) and m.search(r)

                return col

            globs = [makef(re.compile(rex), dir_only, neg) for (neg, rex, dir_only, g) in self._globs]

            def check_glob(e: DirEntry, **kwargs):
                is_dir = e.is_dir()
                r = relpath(e.path, self._root_dir)
                # print("check_glob", e, r, s)
                if not any(m(r, is_dir) for m in globs):
                    return False

            self.on_check_accept(check_glob)
        return super().ready()

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        if self.abs_path:
            print((Path(self._root_dir) / de.path).absolute())
        else:
            super().process_entry(de)


def globre3(g: str, base="", escape=lambda x: ""):

    if g.startswith("!"):
        neg = True
        g = g[1:]
    else:
        neg = None
    if g.endswith("/"):
        g = g[0:-1]
        dirOnly = True
    else:
        dirOnly = None
    i = g.find("/")
    if i < 0:
        atStart = False
    elif i == 0:
        atStart = True
        g = g[1:]
    else:
        atStart = None
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
    if atStart:
        if base:
            res = escape(base) + "/" + res + r"\Z"
        else:
            res = "^" + res + r"\Z"
    else:
        if base:
            res = r"(?ms)\A" + escape(base) + r"/(?:|.+/)" + res + r"\Z"
        else:
            res = r"(?:|.+/)" + res + r"\Z"
        assert atStart in (None, False)
    # from os.path import sep

    # if sep != "/":
    #     res = res.replace("/", escape(sep))

    print("REGX", res, g)

    return (neg, res, dirOnly, g)


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
