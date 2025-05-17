from os.path import dirname, join
from os import rename
from . import ScanTree


class ScanDir(ScanTree):
    def __init__(self) -> None:
        self._de_filter = []
        super().__init__()

    def add_arguments(self, ap):
        self.dry_run = True
        self.bottom_up = True
        self.excludes = []
        self.includes = []
        ap.add_argument("--subs", "-s", action="append", default=[], help="subs regex")
        ap.add_argument("--lower", action="store_true", help="to lower case")
        ap.add_argument("--upper", action="store_true", help="to upper case")
        ap.add_argument(
            "--urlsafe", action="store_true", help="only urlsafe characters"
        )
        if not ap.description:
            ap.description = "Renames files matching re substitution pattern"

        super(ScanDir, self).add_arguments(ap)

    def start(self):
        from re import compile as regex
        import re

        _subs = []

        if self.lower:
            _subs.append((lambda name, parent: name.lower()))

        if self.upper:
            _subs.append((lambda name, parent: name.upper()))

        if self.urlsafe:
            from os.path import splitext

            def slugify(value):
                value = str(value)
                value = re.sub(r"[^a-zA-Z0-9_.+-]+", "_", value)
                return value

            def clean(value):
                value = str(value)
                return re.sub(r"[_-]+", "_", value).strip("_")

            def urlsafe(name, parent):
                s = slugify(name)
                if s != name:
                    assert slugify(s) == s
                    stem, ext = splitext(s)
                    return clean(stem) + ext
                return name

            _subs.append(urlsafe)

        for s in self.subs:
            a = s[1:].split(s[0], 3)
            if len(a) < 2:
                raise RuntimeError("Invalid subtitue pattern `%s'" % s)
            s = 0
            if len(a) > 2:
                for x in a[2]:
                    s |= getattr(re, x.upper())
            # _subs.append((regex(a[0], s), a[1]))
            rex = regex(a[0], s)
            rep = a[1]
            _subs.append((lambda name, parent: rex.sub(rep, name)))
        self._subs = _subs
        super().start()

    def dir_entry(self, de):
        name = de.name
        name2 = name
        parent = dirname(de.path)
        dry_run = self.dry_run

        for fn in self._subs:
            v = fn(name2, parent)
            if v:
                name2 = v

        if name2 and (name != name2):
            try:
                path = join(parent, name)
                dry_run is False and rename(path, join(parent, name2))
            finally:
                print(f'REN: {name!r} -> {name2!r} {dry_run and "?" or "!"} @{parent}')


(__name__ == "__main__") and ScanDir().main()
