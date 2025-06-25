from os import DirEntry
from os.path import abspath
from subprocess import run
from json import loads
from ...walkdir import FileSystemEntry
from ... import FindSkel
from .utils import ffmpeg_supported_extensions, sort_condense
from .query import BooleanResult, FalseResult, create_compiled_searcher

__version__ = "0.0.0"


# ffprobe -v quiet -print_format json -show_format -show_streams "lolwut.mp4" > "lolwut.mp4.json"
class FFQuery(FindSkel):

    def __init__(self):
        self.db: "dict[str, dict[str, object]]" = {}
        self.queries: "list[str]" = []
        self._glob_excludes = []
        self._glob_includes = []

    def add_arguments(self, argp):
        argp.add_argument("-q", dest="queries", action="append", metavar="QUERY", default=[], help="Query")
        return super().add_arguments(argp)

    def check_accept(self, e: DirEntry, depth: int) -> bool:
        return super().check_accept(e, depth=depth) and e.is_file()

    def process_entry(self, de: "DirEntry | FileSystemEntry") -> None:
        fp = run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", de.path], capture_output=True
        )
        data = loads(fp.stdout)
        self.db[abspath(de.path)] = data

    def ready(self) -> None:
        if not self._glob_includes:
            from re import compile

            for k, v in ffmpeg_supported_extensions.items():
                for x in v:
                    self._glob_includes.append(f"*{x}")
        return super().ready()

    def start(self):
        self._walk_paths()

        col = {}

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
                for k, v in o.items():
                    o[k] = check(v, o)
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

        for x in self.queries:
            # q = jmespath.compile(x)
            # pprint.pprint(q)
            q = create_compiled_searcher(x)
            # json.dump(q, stdout, indent=True)
            # print(q)
            for k, v in self.db.items():
                streams = v.get("streams")
                if streams:
                    for s in streams:
                        s = check_stream(s)
                        r = q(s)
                        # print(r, r.__class__)
                        if r:
                            # print(r, s["codec_type"], s.get("codec_name"), v.get("format", {}).get("filename"))
                            try:
                                a = col.setdefault(check(r), {})
                                # print(f"\t{k}")
                                # a[(k, s["index"])] = q
                                a.setdefault(k, set()).add(s["index"])
                                # break
                            except FalseResult:
                                # print("FalseResult")
                                pass
        for r, d in col.items():
            print(r)
            for k, v in d.items():
                a = sorted(v)
                if len(a) > 1:
                    c = sort_condense([(n, n) for n in a])
                    x = ("(" + " ".join([f"{a}-{b}" for a, b in c]) + ")",)
                elif len(a) == 0 or a[0] == 0:
                    x = ()
                else:
                    x = (f"({a[0]})",)
                print(f"\t{k}", *x)


(__name__ == "__main__") and FFQuery().main()
