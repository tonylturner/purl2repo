# purl2repo

purl2repo is a Python library designed to translate Package URLs (purl) into GitHub repository URLs and release information. It supports multiple package managers, including PyPI, npm, and Cargo, and is designed to be easily extendable to other package managers.

## Features
- Supports translating purl for PyPI, npm, and Cargo packages.
- Retrieves GitHub repository information for a specific package and version.
- Easily extensible to support additional package managers.

## Installation
Prerequisites:
- Python 3.7+
- pip (Python package manager)

`This package is not yet published, but soon you can just use pip from pypi`
```bash
pip install purl2repo
```

Installing Locally in Editable Mode
If you are testing or developing the library locally, you can install it in editable mode:

Clone the repository:

```bash
git clone https://github.com/yourusername/purl2repo.git
cd purl2repo
pip install -e .
```

This will install the library and link it to your local development environment, allowing you to make changes and test them immediately.

Usage
Basic Usage Example
You can use the purl2repo library to get repository and release information for different package managers.

```python
from purl2repo import get_source_repo_and_release
```

## Example 

pypi_purl = "pkg:pypi/requests@2.25.1"
result = get_source_repo_and_release(pypi_purl)
print(result)

```python
{
    "package_name": "requests",
    "github_repo": "https://github.com/psf/requests",
    "specified_version": "2.25.1"
}
```

If a GitHub repository is not found, github_repo will be None.

Handling Errors
If the package or version cannot be found, a ValueError will be raised. Make sure to handle this in your code:


## Supported Package Managers
- PyPI: Python Package Index
- npm: Node.js package manager
- Cargo: Rust package manager

## Extending the Library
You can extend the library to support additional package managers by following the same pattern used for the supported managers (PyPI, npm, Cargo). Add a new parser class for the package manager and register it in the manager_registry.py file.

Running Tests
To run the tests, make sure you have unittest installed. Then, you can run all the tests using:

```bash
python -m unittest discover -s tests
```

This will automatically discover and run all test cases in the tests/ directory.

License
This project is licensed under the Apache 2.0 License. See the LICENSE file for details.

Contributing
Contributions are welcome! Feel free to submit pull requests or open issues if you encounter any problems or have suggestions for improvements.