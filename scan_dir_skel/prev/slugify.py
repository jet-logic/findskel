from os import scandir
from pathlib import Path
import re


def slugify(value):
    value = str(value)
    value = re.sub(r"[^a-zA-Z0-9_.+-]+", "_", value)
    return value


def clean(value):
    value = str(value)
    return re.sub(r"[_-]+", "_", value).strip("_")


def dir_entry(entry, ctx):
    p = Path(entry.path)
    if p.is_dir():
        return
    s = slugify(p.name)
    if s != p.name:
        # n =
        # t = clean(s)
        q = Path(s)
        suf = q.suffix
        stm = q.stem
        t = clean(stm) + suf
        # t = s
        print(
            f"{t} <= {p.name}",
            ctx.dry_run,
        )
        assert slugify(t) == t
        if ctx.dry_run is False:
            p.rename(p.with_name(t))
