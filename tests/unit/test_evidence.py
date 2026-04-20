from purl2repo.resolution import evidence


def test_evidence_messages_are_stable():
    assert evidence.fetched("PyPI JSON API") == "Fetched package metadata from PyPI JSON API"
    assert evidence.selected_candidate() == "Selected highest scoring repository candidate"
    assert "Version not supplied" in evidence.skipped_release_no_version()
    assert "Multiple plausible" in evidence.ambiguous_warning()
