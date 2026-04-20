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
- [ ] GitHub release created from `v2.0.0`

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

## v2.0.0 Release

The v2.0.0 release notes are in [docs/releases/v2.0.0.md](releases/v2.0.0.md).

Create the final release only after CI, integration checks, Trivy, and package
build verification are green:

```bash
git tag -a v2.0.0 -m "purl2repo v2.0.0"
git push origin v2.0.0
gh release create v2.0.0 \
  --title "purl2repo v2.0.0" \
  --notes-file docs/releases/v2.0.0.md \
  dist/purl2repo-2.0.0.tar.gz \
  dist/purl2repo-2.0.0-py3-none-any.whl
```

The PyPI publishing workflow also runs on `v*` tags and published GitHub
releases. Confirm Trusted Publishing is configured before tagging the final
release.
