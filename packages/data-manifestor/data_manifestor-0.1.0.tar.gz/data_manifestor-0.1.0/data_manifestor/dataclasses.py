from typing import List, Tuple

from dataclasses import dataclass, field


@dataclass
class Template:

    name: str
    path_prefix: str = "{}-{}-{}"
    path_patterns: list[str] = field(default_factory=list)


@dataclass
class Manifest:

    name: str
    template: Template
    args: tuple[str] = field(default_factory=tuple)
    path_patterns: list[str] = field(default_factory=list)


@dataclass
class LocalComparisonResult:

    manifest: Manifest
    local_dir: str
    resolved_paths: list[tuple[str, list[str]]] = field(default_factory=list)
