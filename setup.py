from setuptools import setup, find_packages

setup(
    name="purl2repo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "packageurl-python",
        "requests",
        "beautifulsoup4",  # Added beautifulsoup4 as a requirement
    ],
    description="A Python library to translate purl to GitHub repos and release information",
    author="Your Name",
    license="Apache-2.0",  # Updated license to Apache 2.0
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",  # Updated classifier for Apache 2.0
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
