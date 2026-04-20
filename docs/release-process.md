# Release Process

## Checklist

- [ ] Version updated in `pyproject.toml`
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
- [ ] GitHub release created from the version tag

## Commands

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest --cov=purl2repo --cov-report=term-missing --cov-fail-under=90
.venv/bin/python -m build
.venv/bin/twine check dist/*
tmpdir="$(mktemp -d)"
python3.11 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install dist/purl2repo-2.0.2-py3-none-any.whl
"$tmpdir/venv/bin/purl2repo" version
```

## Publishing

Publishing is handled by GitHub Actions and should use Trusted Publishing.
Use the TestPyPI workflow for release candidates and the PyPI workflow for final
GitHub releases.

## v2.0.2 Release

The v2.0.2 release notes are in [docs/releases/v2.0.2.md](releases/v2.0.2.md).

Create the final release only after CI, integration checks, Trivy, and package
build verification are green:

```bash
gh release create v2.0.2 \
  --title "purl2repo v2.0.2" \
  --notes-file docs/releases/v2.0.2.md \
  --target main \
  dist/purl2repo-2.0.2.tar.gz \
  dist/purl2repo-2.0.2-py3-none-any.whl
```

## v2.0.1 Release

The v2.0.1 release notes are in [docs/releases/v2.0.1.md](releases/v2.0.1.md).

Create the final release only after CI, integration checks, Trivy, and package
build verification are green:

```bash
gh release create v2.0.1 \
  --title "purl2repo v2.0.1" \
  --notes-file docs/releases/v2.0.1.md \
  --target main \
  dist/purl2repo-2.0.1.tar.gz \
  dist/purl2repo-2.0.1-py3-none-any.whl
```

## v2.0.0 Release

The v2.0.0 release notes are in [docs/releases/v2.0.0.md](releases/v2.0.0.md).

Create the final release only after CI, integration checks, Trivy, and package
build verification are green:

```bash
gh release create v2.0.0 \
  --title "purl2repo v2.0.0" \
  --notes-file docs/releases/v2.0.0.md \
  --target main \
  dist/purl2repo-2.0.0.tar.gz \
  dist/purl2repo-2.0.0-py3-none-any.whl
```

The PyPI publishing workflow runs only when a GitHub release is published.
Confirm Trusted Publishing is configured before publishing the final release.
