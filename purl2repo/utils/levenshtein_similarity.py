import difflib


def levenshtein_similarity(repo_name, package_name):
    """Calculate similarity between the repository name and the package name."""
    return difflib.SequenceMatcher(None, repo_name, package_name).ratio()
