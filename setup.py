from setuptools import setup, find_packages

setup(
    name='purl2repo',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'packageurl-python',
        'requests',
    ],
    description='A Python library to translate purl to GitHub repos and release information',
    author='Your Name',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
