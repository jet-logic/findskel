from os.path import dirname, join
from os import rename
from . import ScanTree


def filesizep(s: str):
    if s[0].isnumeric():
        for i, v in enumerate("bkmgtpezy"):
            if s[-1].lower().endswith(v):
                return int(s[0:-1]) * (2 ** (10 * i))
    return float(s)


def sizerangep(s=""):
    f, _, t = s.partition("..")
    a, b = [filesizep(f) if f else 0, filesizep(t) if t else float("inf")]
    return lambda n: n >= a and n <= b


from argparse import Action, SUPPRESS


class CallAct(Action):

    def __call__(self, parser, namespace, values, *args, **kwargs):
        self.default(values)


class ScanDir(ScanTree):
    def __init__(self) -> None:
        self._de_filter = []
        super().__init__()

    def add_arguments(self, argp):
        self.bottom_up = True
        self.excludes = []
        self.includes = []
        argp.add_argument(
            "--subs", "-s", action="append", default=[], help="subs regex"
        )
        argp.add_argument("--lower", action="store_true", help="to lower case")
        argp.add_argument("--upper", action="store_true", help="to upper case")
        argp.add_argument(
            "--urlsafe", action="store_true", help="only urlsafe characters"
        )
        if not argp.description:
            argp.description = "Renames files matching re substitution pattern"
        fl = self._de_filter
        if 1:

            def fn(values, *args, **kwargs):
                f = sizerangep(values)
                fl.append(lambda e: f(e.stat().st_size))

            argp.add_argument(
                "--sizes",
                action=CallAct,
                default=fn,
                dest=SUPPRESS,
                help="filter sizes",
            )

        super(ScanDir, self).add_arguments(argp)

    def dir_entry(self, de):
        print(de.path)


(__name__ == "__main__") and ScanDir().main()
