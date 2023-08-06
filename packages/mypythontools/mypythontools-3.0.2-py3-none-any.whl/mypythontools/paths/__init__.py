"""Some functions around paths. You can find here `find_path()` to find some path efficiently in
some folder, excluding some other inner folders (like venv, node_modules etc.). There is also function
to get desktop path in posix way.

There is a `wsl_path` class that was just copy pasted from
https://github.com/psychonaute/wsl-pathlib/blob/master/wsl_pathlib/path.py to remove unnecessary requirements.
"""

from mypythontools.paths.paths_internal import (
    find_path,
    get_desktop_path,
    isFolderEmpty,
    is_path_free,
    validate_path,
    PathLike,
)

from mypythontools.paths.wsl_paths import WslPath

__all__ = [
    "find_path",
    "get_desktop_path",
    "isFolderEmpty",
    "is_path_free",
    "validate_path",
    "PathLike",
    "WslPath",
]
