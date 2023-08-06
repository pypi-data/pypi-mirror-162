from setuptools import setup

__version__ = "0.0.1"

NAME = "compr"
CLASSIFIERS = [
    "Programming Language :: Python",
]

setup(
    name=NAME,
    version=__version__,
    package_dir={"": "src"},
    classifiers=CLASSIFIERS,
)
