# Release Process

## Checklist

- [ ] Version updated in `pyproject.toml`
- [ ] Version updated in `src/purl2repo/version.py`
- [ ] Changelog updated
- [ ] README accurate
- [ ] Docs updated
- [ ] Ruff clean
- [ ] Mypy clean
- [ ] Tests green with coverage
- [ ] Build artifacts verified
- [ ] Built wheel installed in a fresh virtual environment
- [ ] TestPyPI publish succeeds
- [ ] PyPI publish workflow ready
- [ ] GitHub release notes prepared

## Commands

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest
.venv/bin/python -m build
tmpdir="$(mktemp -d)"
python3.14 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install dist/purl2repo-2.0.0-py3-none-any.whl
"$tmpdir/venv/bin/purl2repo" version
```

## Publishing

Publishing is handled by GitHub Actions and should use Trusted Publishing.
Use the TestPyPI workflow for release candidates and the PyPI workflow for final
release tags or GitHub releases.
