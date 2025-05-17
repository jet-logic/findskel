from os.path import dirname, join
from os import rename
from . import ScanTree
from re import compile as regex

BEGIN = regex(r"\s*(?:#|\/\*)\s*\<INSERT\s+([^\s\>]+)\s*\>\s*")
END = regex(r"\s*(?:#|\/\*)\s*</INSERT>")


def check(file: str, db: dict[str, dict[str, str]]):
    with open(file, "r") as r:
        it = iter(r)
        try:
            line = next(it, None)
        except UnicodeDecodeError:
            return
        while line is not None:
            m = BEGIN.match(line.rstrip())
            if m:
                n = m.group(1)
                line = next(it, None)
                while line is not None:
                    m = END.match(line.rstrip())
                    if m:
                        db.setdefault(file, {}).setdefault(n, "")
                        # print("INS", n, file)
                        break
                    line = next(it, None)
            line = next(it, None)


def replace(file: str, db: dict[str, str], dry_run: bool):
    lines = []
    with open(file, "r") as r:
        it = iter(r)
        line = next(it, None)
        while line is not None:
            lines.append(line)
            m = BEGIN.match(line)
            if m:
                n = m.group(1)
                line = next(it, None)
                while line is not None:
                    m = END.match(line)
                    if m:
                        # print("END", line)
                        with open(db[n], "r") as r:
                            for line in r:
                                lines.append(line)
                        lines.append(m.string.rstrip() + "\n")
                        break
                    line = next(it, None)
            line = next(it, None)
    if dry_run is False:
        with open(file, "w") as w:
            for line in lines:
                w.write(line)
    else:
        for line in lines:
            print(line, end="")


class ScanDir(ScanTree):
    db: dict[str, dict[str, str]]

    def __init__(self):
        self.db = {}
        self.search: list[str] = []

    def add_arguments(self, ap):
        self.dry_run = True
        self.name_re = []
        self.bottom_up = False
        ap.add_argument(
            "--search", "-s", action="append", default=[], help="search dir for sources"
        )
        if not ap.description:
            ap.description = "Insert/replace lines in text files"

        super(ScanDir, self).add_arguments(ap)

    def start(self):
        from re import compile as regex
        import re

        super().start()

    def dir_entry(self, de):
        if de.is_file():
            check(de.path, self.db)

    def done(self):
        from pathlib import Path

        sd = [Path(d) for d in self.search]

        for file, e in self.db.items():
            for name in e.keys():
                for d in sd:
                    p = d / name
                    if p.is_file():
                        e[name] = str(p)

        for file, e in self.db.items():
            if all(e.values()):
                replace(file, e, self.dry_run)

        # print(self.db)
        return super().done()


(__name__ == "__main__") and ScanDir().main()
