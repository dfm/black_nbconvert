# -*- coding: utf-8 -*-

import json
import shutil
import subprocess as sp
from pathlib import Path


def get_temp_path(subdir=""):
    root = Path(__file__).parent / "data"
    source = root / subdir / "input.ipynb"
    expected = root / subdir / "expected.ipynb"
    target = root / subdir / ".temp.ipynb"
    shutil.copy(source, target)
    return source, target, expected


def compare_notebooks(a, b):
    with open(a, "r") as f:
        str_a = json.dumps(json.load(f), sort_keys=True)
    with open(b, "r") as f:
        str_b = json.dumps(json.load(f), sort_keys=True)
    return str_a == str_b


def test_check():
    source, target, _ = get_temp_path()
    code = sp.call(f"python -m black_nbconvert --check {target}", shell=True)
    assert code != 0
    assert compare_notebooks(source, target)
    target.unlink()


def test_basic():
    _, target, expected = get_temp_path()
    code = sp.call(f"python -m black_nbconvert {target}", shell=True)
    assert code == 0
    assert compare_notebooks(expected, target)
    target.unlink()


def test_config():
    _, target, expected = get_temp_path("config")
    code = sp.call(f"python -m black_nbconvert {target}", shell=True)
    assert code == 0
    assert compare_notebooks(expected, target)
    target.unlink()
