import json
from os import DirEntry
import os
from subprocess import run
from ...walkdir import FileSystemEntry
from ... import FindSkel
import jmespath.lexer

ffmpeg_supported_extensions = {
    # Video Containers
    "video": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".flv",
        ".webm",
        ".m4v",
        ".ts",
        ".mpg",
        ".mpeg",
        ".wmv",
        ".3gp",
        ".ogv",
        ".rm",
        ".rmvb",
        ".vob",
    ],
    # Audio Containers
    "audio": [".mp3", ".aac", ".wav", ".flac", ".ogg", ".oga", ".m4a", ".wma", ".opus", ".ac3", ".amr", ".aiff"],
    # Image Formats
    "image": [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"],
    # Subtitle Formats
    "subtitle": [".srt", ".ass", ".ssa", ".vtt", ".sub"],
    # Raw Streams / Special Formats
    "raw": [".h264", ".h265", ".yuv", ".pcm"],
    # Network/Streaming Protocols (not file extensions, but supported inputs)
    # "protocol": ["rtmp://", "udp://", "tcp://", "http://", "https://"],
}


class FalseResult(Exception):
    pass


class FieldNotFound(Exception):
    pass


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
        data = json.loads(fp.stdout)
        self.db[os.path.abspath(de.path)] = data

    def ready(self) -> None:
        if not self._glob_includes:
            from re import compile

            for k, v in ffmpeg_supported_extensions.items():
                for x in v:
                    self._glob_includes.append(f"*{x}")
        return super().ready()

    def start(self):
        self._walk_paths()
        import jmespath

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
                            print(r, s["codec_type"], s.get("codec_name"), v.get("format", {}).get("filename"))
                            try:
                                a = col.setdefault(check(r), {})
                                # print(f"\t{k}")
                                # a[(k, s["index"])] = q
                                a.setdefault(k, set()).add(s["index"])
                                # break
                            except FalseResult:
                                print("FalseResult")
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


import jmespath
from jmespath.visitor import TreeInterpreter


class BooleanResult:
    """Wrapper for boolean expression results"""

    value: bool
    is_expression: bool = True

    def __init__(self, value: bool):
        assert value is None or isinstance(value, bool), f"value is {value.__class__.__name__}"
        self.value = value

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        if isinstance(other, BooleanResult):
            return self.value == other.value
        return self.value == other

    def __repr__(self):
        return str(1 if self.value else 0)

    def __str__(self):
        return str(1 if self.value else 0)


class NotFoundSentinel:
    """Sentinel value for not found/missing fields"""

    path: str = None  # Optional path information

    # def __init__(self, value: bool):
    #     self.value = value
    def __bool__(self):
        return False

    def __repr__(self):
        return "NOT_FOUND"


NOT_FOUND = NotFoundSentinel()

import jmespath
from jmespath.visitor import TreeInterpreter


class WrappingInterpreter(TreeInterpreter):
    """Interpreter that wraps boolean expression results"""

    def _is_false(self, value):
        # This looks weird, but we're explicitly using equality checks
        # because the truth/false values are different between
        # python and jmespath.
        if isinstance(value, BooleanResult):
            return bool(value) is False
        return value == "" or value == [] or value == {} or value is None or value is False

    def visit_comparator(self, node, value):
        result = super().visit_comparator(node, value)
        return BooleanResult(result)

    def visit_and(self, node, value):
        result = super().visit_and(node, value)
        return BooleanResult(result)

    def visit_or(self, node, value):
        result = super().visit_or(node, value)
        return BooleanResult(result)

    # def visit_not(self, node, value):
    #     result = super().visit_not(node, value)
    #     return BooleanResult(result)
    def visit_not_expression(self, node, value):
        result = super().visit_not_expression(node, value)
        return BooleanResult(result)

    def visit_function_expression(self, node, value):
        result = super().visit_function_expression(node, value)
        # Wrap results from functions that return booleans
        if node["value"] in [
            "contains",
            "ends_with",
            "starts_with",
            "is_empty",
            "is_number",
            "is_string",
            "is_array",
            "is_object",
            "is_boolean",
        ]:
            return BooleanResult(result)
        return result

    # def __init__(self, use_not_found_sentinel=True):
    #     super().__init__()
    #     self.use_not_found_sentinel = use_not_found_sentinel
    # FieldNotFound
    def visit_field(self, node, value):
        # return super().visit_field(node, value)
        return value.get(node["value"])

    # def visit_field(self, node, value):
    #     try:
    #         result = super().visit_field(node, value)
    #         if result is None and self.use_not_found_sentinel:
    #             return NotFoundSentinel(node['value'])
    #         return result
    #     except (AttributeError, KeyError):
    #         return NOT_FOUND

    # def visit_comparator(self, node, value):
    #     result = super().visit_comparator(node, value)
    #     return BooleanResult(result)

    # def visit_and(self, node, value):
    #     left = self.visit(node['children'][0], value)
    #     if isinstance(left, NotFoundSentinel):
    #         return left
    #     if not left:
    #         return BooleanResult(False)
    #     right = self.visit(node['children'][1], value)
    #     return BooleanResult(bool(right))

    # def visit_or(self, node, value):
    #     left = self.visit(node['children'][0], value)
    #     if isinstance(left, NotFoundSentinel):
    #         return left
    #     if left:
    #         return BooleanResult(True)
    #     right = self.visit(node['children'][1], value)
    #     return BooleanResult(bool(right))

    # def visit_not(self, node, value):
    #     result = self.visit(node['children'][0], value)
    #     if isinstance(result, NotFoundSentinel):
    #         return result
    #     return BooleanResult(not result)

    # def visit_index(self, node, value):
    #     try:
    #         return super().visit_index(node, value)
    #     except (IndexError, TypeError):
    #         return NOT_FOUND

    # def visit_slice(self, node, value):
    #     try:
    #         return super().visit_slice(node, value)
    #     except (IndexError, TypeError):
    #         return NOT_FOUND


def create_compiled_searcher(expression_str):
    """Create a compiled search function with boolean wrapping"""
    if not expression_str or not expression_str.strip():
        raise ValueError("Expression string cannot be empty")
    lexer = jmespath.lexer.Lexer()
    toks = lexer.tokenize(expression_str)
    # for t in toks:
    #     print("toks", t)
    #
    parser = jmespath.parser.Parser()
    # parsed = parser.parse(list(toks))
    parsed = parser.parse(expression_str)
    # parsed = parser._do_parse(expression_str)

    interpreter = WrappingInterpreter()

    def search(data):
        return interpreter.visit(parsed.parsed, data)

    print(parsed)

    return search


def sort_condense(ivs: "list[tuple[int, int]]"):
    if len(ivs) == 0:
        return []
    if len(ivs) == 1:
        if ivs[0][0] > ivs[0][1]:
            return [(ivs[0][1], ivs[0][0])]
        else:
            return ivs
    eps: "list[tuple[int,bool]]" = []
    for iv in ivs:
        eps.append((min(iv), False))
        eps.append((max(iv), True))
    eps.sort()
    ret: "list[tuple[int, int]]" = []
    i = level = 0
    while i < len(eps) - 1:
        if not eps[i][1]:
            level = level + 1
            if level == 1:
                left = eps[i][0]
        else:
            if level == 1:
                if not eps[i + 1][1] and eps[i + 1][0] == eps[i][0] + 1:
                    i = i + 2
                    continue
                right = eps[i][0]
                ret.append((left, right))
            level = level - 1
        i = i + 1
    ret.append((left, eps[len(eps) - 1][0]))
    return ret


(__name__ == "__main__") and FFQuery().main()
