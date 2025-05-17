from os import DirEntry, scandir, stat
from os.path import basename, relpath


class PseudoDirEntry:
    __slots__ = ("path", "name")

    def __init__(self, path: str):
        self.path = path
        self.name = basename(self.path)

    def inode(self):
        return self.stat(follow_symlinks=False).st_ino

    def stat(self, follow_symlinks=True):
        return stat(self.path, follow_symlinks=follow_symlinks)

    def is_symlink(self, follow_symlinks=True):
        return (
            self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000
        ) == 0o120000

    def is_dir(self, follow_symlinks=True):
        return (
            self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000
        ) == 0o040000

    def is_file(self, follow_symlinks=True):
        return (self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000) in (
            0o060000,
            0o100000,
            0o010000,
        )


class WalkDir:
    # name_re regex
    follow_symlinks = 0
    bottom_up = False
    carry_on = True
    excludes = None
    includes = None
    _de_filter = None

    def check_accept(self, e: DirEntry):
        if self.includes or self.excludes:
            r = relpath(e.path, self._roor_dir)
            if self.includes:
                if not any(m.search(r) for m in self.includes):
                    return False
            if self.excludes:
                if any(m.search(r) for m in self.excludes):
                    return False
        if self.name_re:
            for m in self.name_re:
                if m.match(e.name):
                    return True
            return False
        if self._de_filter:
            for f in self._de_filter:
                if f(e) is False:
                    return False
        return True

    def check_enter(self, x: DirEntry, depth=None):
        if x.is_dir():
            return self.follow_symlinks > 0 if x.is_symlink() else True

        return False

    def get_iter(self, src):
        try:
            # enter_dir
            yield from scandir(src)
        except FileNotFoundError:
            pass
        except:
            if self.carry_on:
                pass
            else:
                raise
        else:
            pass
            # entered_dir

    def walk_dir_pre(self, src, depth=0):
        depth += 1
        for de in self.get_iter(src):
            if self.check_accept(de):
                yield de
            if self.check_enter(de, depth=depth):
                yield from self.walk_dir_pre(de.path, depth)

    def walk_dir_post(self, src, depth=0):
        depth += 1
        for de in self.get_iter(src):
            if self.check_enter(de, depth=depth):
                yield from self.walk_dir_post(de.path, depth)
            if self.check_accept(de):
                yield de

    def dir_entry_for(self, path):
        return PseudoDirEntry(path)

    def dir_entry(self, de):
        print(de.path)

    def enum_paths(self, paths):
        for p in paths:
            de = self.dir_entry_for(p)
            if de.is_dir():
                self._roor_dir = de.path
                yield from (
                    self.walk_dir_post(p) if self.bottom_up else self.walk_dir_pre(p)
                )
            else:
                yield de

    def walk_roots(self, dirs):
        for x in self.enum_paths(dirs):
            self.dir_entry(x)
