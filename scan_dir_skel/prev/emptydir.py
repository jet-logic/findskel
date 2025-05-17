from os import scandir


def dir_entry(entry, ctx):
    path = entry.path
    if entry.is_dir():
        with scandir(path) as it:
            for entry in it:
                return
        print(entry.path)
