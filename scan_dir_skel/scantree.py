from os import DirEntry
from .main import Main
from .walkdir import WalkDir

__version__ = "0.0.3"


class ScanTree(WalkDir, Main):
    _re_excludes: list[object] | None = None
    _re_includes: list[object] | None = None
    _file_sizes: list[object] | None = None
    _dir_depth: tuple[int, int] | None = None
    _paths_from: list[str] | None = None

    def add_arguments(self, argp):

        group = argp.add_argument_group("Traversal")
        # --depth-first
        group.add_argument(
            "--depth-first",
            action="store_true",
            dest="depth_first",
            help="Process each directory's contents before the directory itself",
        )
        # --follow-symlinks
        group.add_argument(
            "--follow-symlinks",
            dest="follow_symlinks",
            const=1,
            help="Follow symbolic links",
            action="store_const",
        )
        # --act/--dry-run
        try:
            b = self.dry_run
        except AttributeError:
            pass
        else:
            if b:
                argp.add_argument("--act", action="store_false", dest="dry_run", help="not a test run")
            else:
                argp.add_argument(
                    "--dry-run",
                    action="store_true",
                    dest="dry_run",
                    help="test run only",
                )
        # --exclude, --include
        if self._re_excludes is not None or self._re_includes is not None:
            from re import compile as regex

            group.add_argument(
                "--exclude",
                metavar="GLOB",
                action="append",
                type=lambda s: regex(globre(s)),
                dest="_re_excludes",
                help="exclude matching GLOB",
            )
            group.add_argument(
                "--include",
                metavar="GLOB",
                action="append",
                type=lambda s: regex(globre(s)),
                dest="_re_includes",
                help="include matching GLOB",
            )
        # --sizes
        if self._file_sizes is not None:
            group.add_argument(
                "--sizes",
                action="append",
                dest="_file_sizes",
                type=lambda x: sizerangep(x),
                help="Filter sizes: 1k.., 4g, ..2mb",
                metavar="min..max",
            )
        # --depth
        if self._dir_depth is not None:
            group.add_argument(
                "--depth",
                dest="_dir_depth",
                type=lambda x: intrangep(x),
                help="Check for depth: 2.., 4, ..3",
                metavar="min..max",
            )
        # --paths-from
        if self._paths_from is not None:
            group.add_argument(
                "--paths-from",
                metavar="FILE",
                action="append",
                dest="_paths_from",
                default=[],
                help="read list of source-file names from FILE",
            )
        # PATH ...
        argp.add_argument(metavar="PATH", dest="_paths", nargs="*")
        return super().add_arguments(argp)

    def ready(self) -> None:

        if self._re_includes or self._re_excludes:
            from os.path import relpath, sep

            inc = self._re_includes
            exc = self._re_excludes
            # print("ready:check_glob", inc, exc)

            def check_glob(e: DirEntry, **kwargs):
                s = f"{e.path}{sep}" if e.is_dir() else e.path
                r = relpath(s, self._root_dir)
                # print("check_glob", e, r, s)
                if inc:
                    if not any(m.search(r) for m in inc):
                        return False
                if exc:
                    if any(m.search(r) for m in exc):
                        return False

            self.on_check_accept(check_glob)

        sizes: list[tuple[int, int]] = self._file_sizes
        if sizes:

            def check_size(de: DirEntry, **kwargs):
                ok = 0
                n = de.stat().st_size
                for a, b in sizes:
                    if n >= a and n <= b:
                        ok += 1
                return ok > 0

            self.on_check_accept(check_size)

        depth: tuple[int, int] = self._dir_depth
        if depth:
            a, b = depth

            # print("DEPTH", (a, b), file=stderr)

            def check_depth(de: DirEntry, **kwargs):
                d: int = kwargs["depth"]
                # print("check_depth", (d, (a, b)), de.path, file=stderr)
                return d >= a and d <= b

            def enter_depth(de: DirEntry, **kwargs):
                d: int = kwargs["depth"]
                # print("enter_depth", (d, b), de.path, file=stderr)
                return d <= b

            self.on_check_enter(enter_depth)
            self.on_check_accept(check_depth)

        return super().ready()

    def start(self):
        raise DeprecationWarning("Change your code!")
        self.start_walk(self._paths)

    def _walk_paths(self):
        paths_from: list[str] = getattr(self, "_paths_from", None)
        if paths_from:
            for x in paths_from:
                # print(f"_paths_from {x!r}", file=stderr)
                with as_source(x, "r") as f:
                    for e in f:
                        e = e.strip()
                        if e.startswith("#") or not e:
                            continue
                        # print(f"\t- {e!r}", file=stderr)
                        self._start_path(e)
        #
        paths: list[str] = getattr(self, "_paths", None)
        if paths:
            for p in paths:
                self._start_path(p)


def as_source(path="-", mode="rb"):
    if path != "-":
        return open(path, mode)
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


def globre(pat):
    from re import escape, sub
    from os.path import altsep, sep

    SEP = {sep, altsep}
    DSTAR = object()
    RESEP = "[^" + "".join(escape(c) for c in SEP if c) + "]+"

    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    STAR = object()
    res = []
    add = res.append
    i, n = 0, len(pat)
    while i < n:
        c = pat[i]
        i = i + 1
        if c == "*":
            # compress consecutive `*` into one
            if not res:
                add(STAR)
            elif res[-1] is STAR:
                res[-1] = DSTAR
            elif res[-1] is DSTAR:
                pass
            else:
                add(STAR)
        elif c == "?":
            add(".")
        elif c == "[":
            j = i
            if j < n and pat[j] == "!":
                j = j + 1
            if j < n and pat[j] == "]":
                j = j + 1
            while j < n and pat[j] != "]":
                j = j + 1
            if j >= n:
                add("\\[")
            else:
                stuff = pat[i:j]
                if "-" not in stuff:
                    stuff = stuff.replace("\\", r"\\")
                else:
                    chunks = []
                    k = i + 2 if pat[i] == "!" else i + 1
                    while True:
                        k = pat.find("-", k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k + 1
                        k = k + 3
                    chunk = pat[i:j]
                    if chunk:
                        chunks.append(chunk)
                    else:
                        chunks[-1] += "-"
                    # Remove empty ranges -- invalid in RE.
                    for k in range(len(chunks) - 1, 0, -1):
                        if chunks[k - 1][-1] > chunks[k][0]:
                            chunks[k - 1] = chunks[k - 1][:-1] + chunks[k][1:]
                            del chunks[k]
                    # Escape backslashes and hyphens for set difference (--).
                    # Hyphens that create ranges shouldn't be escaped.
                    stuff = "-".join(s.replace("\\", r"\\").replace("-", r"\-") for s in chunks)
                # Escape set operations (&&, ~~ and ||).
                stuff = sub(r"([&~|])", r"\\\1", stuff)
                i = j + 1
                if not stuff:
                    # Empty range: never match.
                    add("(?!)")
                elif stuff == "!":
                    # Negated empty range: match any character.
                    add(".")
                else:
                    if stuff[0] == "!":
                        stuff = "^" + stuff[1:]
                    elif stuff[0] in ("^", "["):
                        stuff = "\\" + stuff
                    add(f"[{stuff}]")
        else:
            add(escape(c))
    assert i == n

    # Deal with STARs.
    inp = res
    res = []
    add = res.append
    i, n = 0, len(inp)
    # Fixed pieces at the start?
    while i < n and inp[i] not in (STAR, DSTAR):
        add(inp[i])
        i += 1
    # Now deal with STAR fixed STAR fixed ...
    # For an interior `STAR fixed` pairing, we want to do a minimal
    # .*? match followed by `fixed`, with no possibility of backtracking.
    # Atomic groups ("(?>...)") allow us to spell that directly.
    # Note: people rely on the undocumented ability to join multiple
    # translate() results together via "|" to build large regexps matching
    # "one of many" shell patterns.
    while i < n:
        assert inp[i] in (STAR, DSTAR)
        STA = inp[i]
        PAT = RESEP if STA is STAR else ".*"
        i += 1
        if i == n:
            add(PAT)
            break
        assert inp[i] not in (STAR, DSTAR)
        fixed = []
        while i < n and inp[i] not in (STAR, DSTAR):
            fixed.append(inp[i])
            i += 1
        fixed = "".join(fixed)
        if i == n:
            add(PAT)
            add(fixed)
        elif STA is DSTAR:
            add(f"{PAT}{fixed}")
        else:
            add(f"{PAT}{fixed}")
    assert i == n
    res = "".join(res)
    return rf"(?s:{res})\Z"


def filesizep(s: str):
    if s[0].isnumeric():
        q = s.lower().rstrip("b")
        for i, v in enumerate("kmgtpezy"):
            if q[-1].endswith(v):
                return float(q[0:-1]) * (2 ** (10 * (i + 1)))
        return float(q)
    return float(s)


def sizerangep(s=""):
    f, d, t = s.partition("..")
    if d:
        a, b = [filesizep(f) if f else 0, filesizep(t) if t else float("inf")]
        return (a, b)
    elif f:
        c = filesizep(f)
        return (c, c)
    else:
        return (0, float("inf"))


def intrangep(s=""):
    f, d, t = s.partition("..")
    if d:
        a, b = [int(f) if f else 0, int(t) if t else float("inf")]
        return (a, b)
    elif f:
        c = int(f)
        return (c, c)
    else:
        return (0, float("inf"))
