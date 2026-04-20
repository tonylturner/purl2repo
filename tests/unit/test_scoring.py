from purl2repo.models import RepositoryCandidate
from purl2repo.purl.parse import parse_purl
from purl2repo.resolution.scorer import confidence_from_score, score_candidates


def test_scoring_prefers_structured_source_repo():
    parsed = parse_purl("pkg:pypi/requests@2.31.0")
    candidates = score_candidates(
        [
            RepositoryCandidate(
                url="https://requests.readthedocs.io",
                normalized_url="https://requests.readthedocs.io",
                host="requests.readthedocs.io",
                repository_type="generic_git",
                source="homepage",
                score=0.0,
                reasons=["Homepage field"],
            ),
            RepositoryCandidate(
                url="git+https://github.com/psf/requests.git",
                normalized_url="git+https://github.com/psf/requests.git",
                host="github.com",
                repository_type="github",
                source="project_urls_source",
                score=0.0,
                reasons=["Candidate from project_urls['Source']"],
            ),
        ],
        parsed,
    )

    assert candidates[0].normalized_url == "https://github.com/psf/requests"
    assert candidates[0].score >= 90
    assert "Recognized github hosting provider" in candidates[0].reasons


def test_confidence_mapping():
    assert confidence_from_score(95) == "high"
    assert confidence_from_score(70) == "medium"
    assert confidence_from_score(40) == "low"
    assert confidence_from_score(5) == "none"


def test_scoring_penalizes_bad_and_weak_candidates():
    parsed = parse_purl("pkg:pypi/requests")
    candidates = score_candidates(
        [
            RepositoryCandidate(
                url="notaurl",
                normalized_url="notaurl",
                host="",
                repository_type="generic_git",
                source="metadata_page",
                score=0.0,
                reasons=["bad"],
            ),
            RepositoryCandidate(
                url="https://github.com/psf",
                normalized_url="https://github.com/psf",
                host="github.com",
                repository_type="github",
                source="metadata_page",
                score=0.0,
                reasons=["org root"],
            ),
        ],
        parsed,
    )

    assert candidates[-1].score == 0
    assert any("Malformed" in reason for reason in candidates[-1].reasons)
    assert any("organization root" in reason for reason in candidates[0].reasons)


def test_maven_parent_scm_is_capped_below_high_confidence():
    parsed = parse_purl("pkg:maven/com.google.j2objc/j2objc-annotations@1.1")
    candidates = score_candidates(
        [
            RepositoryCandidate(
                url="https://github.com/example/parent",
                normalized_url="https://github.com/example/parent",
                host="github.com",
                repository_type="github",
                source="pom_parent_scm",
                score=0.0,
                reasons=["Candidate from Maven parent scm.url"],
            )
        ],
        parsed,
    )

    assert confidence_from_score(candidates[0].score) == "medium"
    assert any("Inherited Maven parent SCM" in reason for reason in candidates[0].reasons)


def test_scraped_candidates_without_specific_package_match_do_not_resolve():
    parsed = parse_purl("pkg:maven/org.apache.tomcat/tomcat-jdbc@9.0.16")
    candidates = score_candidates(
        [
            RepositoryCandidate(
                url="https://github.com/apache/tomcat-jakartaee-migration",
                normalized_url="https://github.com/apache/tomcat-jakartaee-migration",
                host="github.com",
                repository_type="github",
                source="scrape",
                score=0.0,
                reasons=["Candidate from fallback scraper"],
            )
        ],
        parsed,
    )

    assert confidence_from_score(candidates[0].score) == "none"
    assert any("does not match package name" in reason for reason in candidates[0].reasons)
