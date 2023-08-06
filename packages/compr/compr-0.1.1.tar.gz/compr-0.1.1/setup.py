from setuptools import setup

__version__ = "0.1.1"

NAME = "compr"
CLASSIFIERS = [
    "Programming Language :: Python",
]

setup(
    name=NAME,
    version=__version__,
    package_dir={"": "src"},
    classifiers=CLASSIFIERS,
    long_description_content_type='text/markdown',
)
