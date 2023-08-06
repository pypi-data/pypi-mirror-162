import os
from glob import glob

from .dataclasses import LocalComparisonResult, Manifest
from .paths import generate_path_pattern, resolve_paths
from .transformers import dict_to_template


def generate_manifest(template_dict: dict, *args: str) -> Manifest:
    template = dict_to_template(template_dict)
    return Manifest(
        name=template.name,
        template=template,
        args=args,
        path_patterns=[
            generate_path_pattern(template.path_prefix, path_pattern, *args)
            for path_pattern in template.path_patterns
        ],
    )


def compare_manifest_to_local(
    template_dict: dict, local_dir: str, *args: str
) -> LocalComparisonResult:
    manifest = generate_manifest(template_dict, *args)
    return LocalComparisonResult(
        local_dir=local_dir,
        manifest=manifest,
        resolved_paths=[
            resolve_paths(local_dir, path_pattern)
            for path_pattern in manifest.path_patterns
        ],
    )
