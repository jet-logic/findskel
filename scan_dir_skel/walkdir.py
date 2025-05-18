import re
from os import DirEntry, scandir, stat, stat_result
from os.path import basename, relpath
from typing import List, Optional, Callable, Generator

__version__ = "0.0.2"


class FileSystemEntry:
    __slots__ = ("path", "name")

    def __init__(self, path: str) -> None:
        self.path: str = path
        self.name: str = basename(self.path)

    def inode(self) -> int:
        return self.stat(follow_symlinks=False).st_ino

    def stat(self, follow_symlinks: bool = True) -> stat_result:
        return stat(self.path, follow_symlinks=follow_symlinks)

    def is_symlink(self, follow_symlinks: bool = True) -> bool:
        return (
            self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000
        ) == 0o120000

    def is_dir(self, follow_symlinks: bool = True) -> bool:
        return (
            self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000
        ) == 0o040000

    def is_file(self, follow_symlinks: bool = True) -> bool:
        return (self.stat(follow_symlinks=follow_symlinks).st_mode & 0o170000) in (
            0o060000,
            0o100000,
            0o010000,
        )


class WalkDir:
    follow_symlinks: int = 0
    bottom_up: bool = False
    carry_on: bool = True
    excludes: Optional[List[re.Pattern[str]]] = None
    includes: Optional[List[re.Pattern[str]]] = None
    max_depth: int = -1  # Default to -1 for no limit
    _root_dir: str = ""
    _check_accept: tuple[object, tuple[object, object] | None] | None = None
    _check_enter: tuple[object, tuple[object, object] | None] | None = None

    def check_accept(self, e: DirEntry, depth: int = -1) -> bool:
        cur = self._check_accept
        while cur is not None:
            check, then = cur
            if check(e, depth=depth) is False:
                return False
            cur = then
        return True

    def on_check_accept(self, f: Callable[[DirEntry, int], bool]):
        self._check_accept = (f, self._check_accept)

    def on_check_enter(self, f: Callable[[DirEntry, int], bool]):
        self._check_enter = (f, self._check_enter)

    def check_enter(self, x: DirEntry, depth: int = -1) -> bool:
        if not x.is_dir():
            return False
        if self.max_depth != -1 and depth is not None and depth > self.max_depth:
            return False
        if x.is_symlink():
            if not (self.follow_symlinks > 0):
                return False
        cur = self._check_enter
        while cur is not None:
            check, then = cur
            if check(x, depth=depth) is False:
                return False
            cur = then
        return True

    def scan_directory(self, src: str) -> Generator[DirEntry, None, None]:
        try:
            # enter_dir
            it = scandir(src)
        except FileNotFoundError:
            pass
        except Exception:
            if self.carry_on:
                pass
            else:
                raise
        else:
            yield from it

    def walk_top_down(
        self, src: str, depth: int = 0
    ) -> Generator[DirEntry, None, None]:
        depth += 1
        for de in self.scan_directory(src):
            if self.check_accept(de, depth):
                yield de
            if self.check_enter(de, depth):
                yield from self.walk_top_down(de.path, depth)

    def walk_bottom_up(
        self, src: str, depth: int = 0
    ) -> Generator[DirEntry, None, None]:
        depth += 1
        for de in self.scan_directory(src):
            if self.check_enter(de, depth):
                yield from self.walk_bottom_up(de.path, depth)
            if self.check_accept(de, depth):
                yield de

    def create_entry(self, path: str) -> FileSystemEntry:
        return FileSystemEntry(path)

    def process_entry(self, de: DirEntry | FileSystemEntry) -> None:
        print(de.path)

    def iterate_paths(
        self, paths: List[str]
    ) -> Generator[DirEntry | FileSystemEntry, None, None]:
        for p in paths:
            de: FileSystemEntry = self.create_entry(p)
            if de.is_dir():
                self._root_dir = de.path
                yield from (
                    self.walk_bottom_up(p) if self.bottom_up else self.walk_top_down(p)
                )
            else:
                self._root_dir = ""
                yield de

    def start_walk(self, dirs: List[str]) -> None:
        for x in self.iterate_paths(dirs):
            self.process_entry(x)
