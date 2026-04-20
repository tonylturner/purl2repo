# purl-spec Type Fixtures

These JSON files are vendored from the upstream Package URL specification test
fixtures:

<https://github.com/package-url/purl-spec/tree/main/tests/types>

Only fixtures for PURL types supported by `purl2repo` are included. The upstream
project is MIT licensed; see:

<https://github.com/package-url/purl-spec/blob/main/LICENSE>

When support for a new PURL type is added, copy that type's upstream fixture
into this directory and add it to `SUPPORTED_TYPE_FIXTURES` in
`tests/unit/test_purl_spec_examples.py`.
