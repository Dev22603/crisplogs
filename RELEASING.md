# Releasing crisplogs

Maintainer notes for cutting a new release. Run from the repo root.

## 1. Bump the version

Edit **`crisplogs/__init__.py`** — `__version__` is the single source of truth.
`pyproject.toml` reads it dynamically; the README badge fetches live from PyPI.

```python
__version__ = "0.3.1"
```

Also update `CHANGELOG.md` with the new version's notes.

## 2. Clean old build artifacts

```bash
rm -rf dist/ build/ *.egg-info
```

## 3. Install build tools (one-time)

```bash
pip install --upgrade build twine
```

## 4. Build sdist + wheel

```bash
python -m build
```

Produces `dist/crisplogs-<version>.tar.gz` and `dist/crisplogs-<version>-py3-none-any.whl`.

## 5. Sanity-check artifacts

```bash
twine check dist/*
```

## 6. (Recommended) Test on TestPyPI first

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --no-deps crisplogs==<version>
```

## 7. Publish to PyPI

```bash
twine upload dist/*
```

Username: `__token__`
Password: a `pypi-...` API token from https://pypi.org/manage/account/token/

To skip the prompt, store the token in `~/.pypirc` or set `TWINE_PASSWORD`.

## 8. Tag the release

```bash
git tag v<version>
git push --tags
```

## One-liner (after version bump)

```bash
rm -rf dist/ build/ *.egg-info && python -m build && twine check dist/* && twine upload dist/*
```
