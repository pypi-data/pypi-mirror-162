from typing import List, Tuple

import os
from glob import glob


class PathException(Exception):
    """Pathing related Exception for more specific error handling."""


def resolve_paths(
    parent_dir: str,
    path_pattern: str,
) -> tuple[str, list[str]]:
    path = os.path.join(parent_dir, path_pattern)
    return (
        path,
        glob(path),
    )


def generate_path_pattern(
    path_prefix: str,
    path_pattern: str,
    *args,
) -> str:
    full_pattern = path_prefix + path_pattern

    try:
        return full_pattern.format(*args)
    except IndexError:
        raise PathException(
            "Incompatible path_pattern and args combination. path_pattern=%s, args=%s",
            full_pattern,
            args,
        )
