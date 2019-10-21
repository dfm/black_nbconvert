#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["__version__", "BlackPreprocessor"]

import os
import sys
from pathlib import Path

import toml
import nbformat
from nbconvert.preprocessors import Preprocessor
from black import (
    find_project_root,
    FileMode,
    format_str,
    InvalidInput,
    DEFAULT_LINE_LENGTH,
)

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = None


class BlackPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        self.mode = FileMode(*args, **kwargs)
        super(BlackPreprocessor, self).__init__()

    def preprocess(self, *args, **kwargs):
        self.count = 0
        return super(BlackPreprocessor, self).preprocess(*args, **kwargs)

    def preprocess_cell(self, cell, resources, index):
        if cell.get("cell_type", None) == "code":
            src = cell.get("source", "")
            if len(src.strip()):
                try:
                    cell["source"] = format_str(src, mode=self.mode).strip()
                except InvalidInput:
                    pass
                if src.strip()[-1] == ";":
                    cell["source"] += ";"
                if src != cell["source"]:
                    self.count += 1

        return cell, resources


def format_one(proc, filename, check=False):
    with open(filename) as f:
        notebook = nbformat.read(f, as_version=4)
    proc.preprocess(
        notebook,
        {"metadata": {"path": os.path.dirname(os.path.abspath(filename))}},
    )
    if not check:
        with open(filename, mode="wt") as f:
            nbformat.write(notebook, f)
    return proc.count > 0


def format_some(filenames, **config):
    check = config.get("check", False)
    root = find_project_root(filenames)
    path = root / "pyproject.toml"
    if path.is_file():
        value = str(path)
        pyproject_toml = toml.load(value)
        new_config = pyproject_toml.get("tool", {}).get("black", {})
        config = dict(new_config, **config)

    proc = BlackPreprocessor(
        line_length=config.get("line_length", DEFAULT_LINE_LENGTH),
        target_versions=set(config.get("target_version", [])),
        string_normalization=not config.get(
            "skip_string_normalization", False
        ),
    )

    count = 0
    for filename in filenames:
        changed = format_one(proc, filename, check=check)
        if changed:
            count += 1
            if check:
                print("Invalid format: {0}".format(filename))
            else:
                print("Formatted: {0}".format(filename))

    return count


def main():
    import re
    import argparse

    parser = argparse.ArgumentParser(
        description="Format Jupyter notebooks using black"
    )
    parser.add_argument(
        "filenames", nargs="+", help="files or directories to format"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="just check the formatting, don't overwrite",
    )
    args = parser.parse_args()

    check = args.check

    exclude_re = re.compile(r"/(\.ipynb_checkpoints)/")
    filenames = []
    for fn in args.filenames:
        path = Path(os.path.abspath(fn))
        if path.is_dir():
            filenames += list(
                str(fn)
                for fn in path.glob("**/*.ipynb")
                if not exclude_re.search(str(fn))
            )
        else:
            filenames.append(str(path))

    count = format_some(tuple(filenames), check=check)
    if count > 0:
        if check:
            print("{0} notebook(s) would be formatted".format(count))
        else:
            print("Formatted {0} notebook(s)".format(count))
    if check:
        return count
    return 0


if __name__ == "__main__":
    sys.exit(main())
