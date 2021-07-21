# black + nbconvert

Tired of having to *think* about formatting in Jupyter notebooks?
Look no further!
This script will correctly format your Jupyter notebooks for you using [black](https://black.readthedocs.io).

**Warning: This project will overwrite your notebooks in place.
It shouldn't change anything except the format, but use at your own risk!**

## Installation & Usage

To install:

```bash
pip install black_nbconvert
```

To check a notebook:

```bash
black_nbconvert --check /path/to/a/notebook.ipynb
```

To fix the formatting in a notebook (in place):

```bash
black_nbconvert /path/to/a/notebook.ipynb
```

If you pass a directory instead of a notebook file, notebooks will be found recursively below that directory.
For example:

```bash
black_nbconvert .
```

will fix the formatting for all notebooks in the current directory and (recursively) below.

*Configuration:* Configuration for `black` in a `pyproject.toml` file above the target files will be respected.

## Version control integration

Use [pre-commit](https://pre-commit.com/).
Once you [have it installed](https://pre-commit.com/#install), add this to the `.pre-commit-config.yaml` in your repository:

```yaml
repos:
- repo: https://github.com/dfm/black_nbconvert
  rev: v0.3.0
  hooks:
  - id: black_nbconvert
```

Then run `pre-commit install` and you're ready to go.
