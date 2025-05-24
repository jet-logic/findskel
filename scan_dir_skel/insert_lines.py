from os import DirEntry
from re import compile as regex
from .walkdir import FileSystemEntry
from .scantree import ScanTree

BEGIN = regex(r"\s*(?:#|\/\*+)\s*(?:<INSERT\s+([^\s\>]+)\s*\>|<<<\s+([^\s]+))\s*")
END = regex(r"\s*(?:#|\/\*|)\s*(?:</INSERT>|>>>)")


def check(file: str, db: dict[str, dict[str, str]]):
    # print("CHECK", file)
    with open(file, "r") as r:
        it = iter(r)
        try:
            line = next(it, None)
        except UnicodeDecodeError:
            return
        while line is not None:
            m = BEGIN.match(line.rstrip())
            if m:
                n = m.group(1) or m.group(2)
                # print("BEGIN", n, m)
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
                n = m.group(1) or m.group(2)
                line = next(it, None)
                while line is not None:
                    m = END.match(line)
                    if m:
                        # print("END", n, db[n])
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


class InsertLines(ScanTree):
    def __init__(self):
        self.db: dict[str, dict[str, str]] = {}
        self.search: list[str] = []
        self.dry_run = True

    def add_arguments(self, argp):
        argp.add_argument(
            "--search",
            "-s",
            action="append",
            metavar="DIR",
            default=[],
            help="Search dir for sources",
        )
        if not argp.description:
            argp.description = "Insert/replace lines in text files"
        return super().add_arguments(argp)

    def check_accept(self, e: DirEntry) -> bool:
        return super().check_accept(e) and e.is_file()

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        return check(de.path, self.db)

    def done(self) -> None:
        from sys import stderr
        from pathlib import Path

        sd = [Path(d) for d in self.search]

        for file, e in self.db.items():
            for name in e.keys():
                for d in sd:
                    p = d / name
                    if p.is_file():
                        e[name] = str(p)

        for file, e in self.db.items():
            seen = None
            for k, v in e.items():
                if v:
                    continue
                elif seen is None:
                    seen = True
                    print("Error:", file, file=stderr)
                print("\t- Missing", k, file=stderr)

            if all(e.values()):
                replace(file, e, self.dry_run)

        return super().done()

    def start(self):
        self._walk_paths()


(__name__ == "__main__") and InsertLines().main()
