from os import scandir
from pathlib import Path


def dir_entry(entry, ctx):
    path = entry.path
    if entry.is_dir():
        try:
            with scandir(path) as it:
                for entry in it:
                    return
        except OSError:
            return
        rd(path)


def rd(path):
    p = Path(path)
    if not p.is_dir():
        return
    try:
        with scandir(path) as it:
            for entry in it:
                return
    except OSError:
        return
    print("RM", p)
    p.rmdir()
    if p.parent != p:
        rd(str(p))
