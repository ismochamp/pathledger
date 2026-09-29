#!/usr/bin/env python3
"""Materialize labelled path-audit inputs only on a POSIX filesystem."""
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent


def generate_fixture(destination=None):
    if os.name == "nt":
        raise RuntimeError("The synthetic fixture uses Windows-invalid filenames; generate it on a POSIX filesystem only.")
    target = Path(destination) if destination is not None else BASE / "runtime" / "operations-archive"
    # Refuse symlinked ancestors before creating any directories or files.
    for parent in [target, *target.parents]:
        if parent.is_symlink():
            raise ValueError("The fixture destination must not contain symlinks.")
    target.mkdir(parents=True, exist_ok=True)
    records = json.loads((BASE / "fixtures" / "archive_manifest.json").read_text(encoding="utf-8"))
    for relative, content in records.items():
        parts = Path(relative).parts
        if Path(relative).is_absolute() or not parts or any(p in (".", "..") for p in parts):
            raise ValueError("Fixture paths must remain relative to the destination.")
        output = target / relative
        for parent in [output, *output.parents]:
            if parent.is_symlink():
                raise ValueError("The fixture destination must not contain symlinks.")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            if not output.is_file() or output.read_text(encoding="utf-8") != content:
                raise ValueError("An existing file differs from the synthetic fixture; move it before retrying.")
        else:
            with output.open("x", encoding="utf-8") as handle:
                handle.write(content)
    return target


if __name__ == "__main__":
    try:
        print(generate_fixture())
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit(str(error))
