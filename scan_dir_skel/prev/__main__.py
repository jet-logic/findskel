from .walkdir import WalkDir


def main(app):

    def enum_modules():
        if app.modules:
            from importlib import import_module
            from re import compile as RE

            mod_re = RE(r"^\w+[\w\d\.]+$")
            for x in app.modules:
                if mod_re.match(x):
                    yield import_module(x)
                else:
                    yield load_module(x)

    mods = list(enum_modules())

    # walk_start
    if mods:
        for m in mods:
            f = getattr(m, "walk_start", None)
            if f:
                f(ctx=app)
    # walk_dir = walk_dir_post if app.bottom_up else walk_dir_pre
    for d in app.paths:
        app.root_dir = d
        # st = ScanTree()
        st = WalkDir()
        st.name_re = []
        st.follow_symlinks = app.follow_symlinks

        # print("WALK", [(x.__name__) for x in mods])
        for x in st.walk_dir_post(d) if app.bottom_up else st.walk_dir_pre(d):
            if mods:
                for m in mods:
                    f = getattr(m, "dir_entry", None)
                    if f:
                        f(entry=x, ctx=app)
            else:
                print(x.path)
    # walk_end
    if mods:
        for m in mods:
            f = getattr(m, "walk_end", None)
            if f:
                f(ctx=app)


if __name__ == "__main__":

    from ocli import ArgumentParser

    main(
        ArgumentParser(prog="scandir")
        .args("paths", metavar="DIR")
        .flag("verbose", "v")
        .flag("dry-run", "n", dest="dry_run", default=None, help="test run only")
        .off("act", "a", dest="dry_run", help="not a test run")
        .flag(
            "bottom-up",
            "depth",
            help="Process  each  directory's contents before the directory itself",
        )
        .const(
            "P",
            dest="follow_symlinks",
            const=0,
            default=0,
            help="Never follow symbolic links. This is the default behaviour",
        )
        .const("L", dest="follow_symlinks", const=1, help="Follow symbolic links")
        .const(
            "H",
            dest="follow_symlinks",
            const=-1,
            help="Do not follow symbolic links, except while processing  the  command line arguments",
        )
        .append(
            "module",
            "m",
            dest="modules",
            help="plugin module",
        )
        .append(
            "set",
            dest="vars",
            help="set a variable",
        )
        .parse_args()
    )


def load_module(value):
    from imp import find_module, load_module
    from os.path import splitext, basename, isfile, dirname

    (mo, parent, title) = (None, dirname(value), basename(value))
    if isfile(value):
        (title, _) = splitext(title)
    if parent:
        mo = find_module(title, [parent])
    else:
        mo = find_module(title)
    if mo:
        mo = load_module(title, *mo)
    return mo
