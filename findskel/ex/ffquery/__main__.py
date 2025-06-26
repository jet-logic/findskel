from os import DirEntry
from os.path import abspath
from subprocess import run
from json import loads

from ...main import flag
from ...walkdir import FileSystemEntry
from ... import FindSkel
from .utils import ffmpeg_supported_extensions, sort_condense
from .query import BooleanResult, FalseResult, FieldNotFound, create_compiled_searcher

__version__ = "0.0.0"


# ffprobe -v quiet -print_format json -show_format -show_streams "media.mp4" > "media.mp4.json"
class FFQuery(FindSkel):
    which: str = flag("which", "which files: video, audio, image, subtitle", metavar="TYPE")
    ffprobe: str = flag("bin", "ffprobe location", metavar="BIN")

    def __init__(self):
        self.db: "dict[str, dict[str, object]]" = {}
        self.queries: "list[str]" = []
        self._glob_excludes = []
        self._glob_includes = []
        self.which = ""

    def add_arguments(self, argp):
        argp.add_argument("-q", dest="queries", action="append", metavar="QUERY", default=[], help="Query")
        return super().add_arguments(argp)

    def check_accept(self, e: DirEntry, depth: int) -> bool:
        return super().check_accept(e, depth=depth) and e.is_file()

    def process_entry(self, de: "DirEntry | FileSystemEntry") -> None:
        fp = run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", de.path], capture_output=True
        )
        if fp.returncode == 0:
            data = loads(fp.stdout)
            self.db[abspath(de.path)] = data
        else:
            print(f"Failed to probe {de.path}")

    def ready(self) -> None:
        if not self._glob_includes:
            w = tuple(x.strip() for x in self.which.strip().split(","))

            for k, v in ffmpeg_supported_extensions.items():
                if w and k not in w:
                    continue
                for x in v:
                    self._glob_includes.append(f"*{x}")
        return super().ready()

    def start(self):
        self._walk_paths()

        def seive(o):
            if isinstance(o, BooleanResult):
                if o.value:
                    return False
                raise FalseResult()
            return True

        def check(o, parent=None):
            if isinstance(o, list):
                return tuple(check(x, o) for x in filter(seive, o))
            elif isinstance(o, dict):
                return tuple((k, check(v, o)) for k, v in o.items())
            elif isinstance(o, BooleanResult):
                if o.value:
                    return o.value
                raise FalseResult()
            return o

        def check_stream(s: "dict[str,object]"):
            if s.get("codec_type") == "video":
                v = s.get("avg_frame_rate") or s.get("r_frame_rate")
                if isinstance(v, str):
                    n, _, d = v.rpartition("/")
                    if _:
                        try:
                            s["_fps"] = float(n) / float(d)
                        except Exception:
                            pass
            return s

        col: "dict[object, dict[str,set[int]]]" = {}

        for x in self.queries:
            q_format = q_root = ""
            if x.startswith("f[") and x.endswith("]"):
                q_format = x[1:]
            elif x.startswith("r[") and x.endswith("]"):
                q_root = x[1:]
            if q_format:
                q = create_compiled_searcher(q_format)
                for path, info in self.db.items():
                    format = info.get("format", {})
                    try:
                        r = q(format)
                    except FieldNotFound:
                        continue
                    else:
                        if r:
                            try:
                                a = col.setdefault(check(r), {})
                                a.setdefault(path, set()).add(-1)
                            except FalseResult:
                                pass
            elif q_root:
                q = create_compiled_searcher(q_root)
                for path, info in self.db.items():
                    try:
                        r = q(info)
                    except FieldNotFound:
                        continue
                    else:
                        if r:
                            try:
                                a = col.setdefault(check(r), {})
                                a.setdefault(path, set()).add(-1)
                            except FalseResult:
                                pass
            else:
                q = create_compiled_searcher(x)

                # json.dump(q, stdout, indent=True)
                # print(q)
                for path, info in self.db.items():
                    streams: "list[dict[str,object]]" = info.get("streams", [])
                    for stream in streams:
                        stream = check_stream(stream)
                        try:
                            r = q(stream)
                        except FieldNotFound:
                            continue
                        # print(r, r.__class__)
                        if r:
                            # print(r, s["codec_type"], s.get("codec_name"), v.get("format", {}).get("filename"))
                            try:
                                a = col.setdefault(check(r), {})
                                # print(f"\t{k}")
                                # a[(k, s["index"])] = q
                                a.setdefault(path, set()).add(stream["index"])
                                # break
                            except FalseResult:
                                # print("FalseResult")
                                pass

        tab = "\t"
        for r, d in col.items():
            print(r)
            for path, info in d.items():
                a = sorted(info)
                if len(a) > 1:
                    x = ("(" + " ".join([f"{a}-{b}" for a, b in sort_condense([(n, n) for n in a])]) + ")",)
                elif len(a) == 0 or all(n <= 0 for n in a):
                    x = ()
                else:
                    x = (f"({a[0]})",)
                print(f"{tab}{path}", *x)


(__name__ == "__main__") and FFQuery().main()
