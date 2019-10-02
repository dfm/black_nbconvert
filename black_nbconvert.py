#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["__version__", "BlackPreprocessor"]

import os
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

from _version import version as __version__


class BlackPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        self.mode = FileMode(*args, **kwargs)
        super(BlackPreprocessor, self).__init__()

    def preprocess_cell(self, cell, resources, index):
        if cell.get("cell_type", None) == "code":
            src = cell.get("source", "")
            if len(src.strip()):
                try:
                    cell["source"] = format_str(src, mode=self.mode)
                except InvalidInput:
                    pass
                if cell["source"][-1] == "\n" and src[-1] != "\n":
                    cell["source"] = cell["source"][:-1]
        return cell, resources


def format_one(proc, filename):
    with open(filename) as f:
        notebook = nbformat.read(f, as_version=4)
    proc.preprocess(
        notebook,
        {"metadata": {"path": os.path.dirname(os.path.abspath(filename))}},
    )
    with open(filename, mode="wt") as f:
        nbformat.write(notebook, f)


def format_some(filenames, **config):
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

    for filename in filenames:
        format_one(proc, filename)


def main():
    import re
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    filenames = []
    if args.root is not None:
        exclude_re = re.compile(r"/(\.ipynb_checkpoints)/")
        filenames = list(
            str(fn)
            for fn in Path(os.path.abspath(args.root)).glob("**/*.ipynb")
            if not exclude_re.search(str(fn))
        )
    filenames += args.filenames

    format_some(tuple(filenames))


if __name__ == "__main__":
    main()
