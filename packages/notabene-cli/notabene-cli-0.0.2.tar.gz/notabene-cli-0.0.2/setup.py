#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: Jeroen Peter Bos <jeroen@notabene.cloud>
"""

import importlib.util
from os import path
from pathlib import Path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.in"), encoding="utf-8") as f:
    requirements = f.read().split("# DEVELOPMENT REQUIREMENTS")[0].split("\n")


# Get the base version from the library.  (We'll find it in the `version.py`
# file in the src directory, but we'll bypass actually loading up the library.)
vspec = importlib.util.spec_from_file_location(
    "version", str(Path(__file__).resolve().parent / "notabene" / "version.py")
)
vmod = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, "__version__")

setup(
    name="notabene-cli",
    description="The command line interface for interacting with notabene.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=version,
    install_requires=requirements,
    entry_points="""
    [console_scripts]
    notabene=notabene.cli:cli
    """,
    python_requires=">=0.0.1",
    author="Jeroen Peter Bos",
    author_email="jeroen@notabene.cloud",
    # Use the URL to the github repo.
    url="https://github.com/JeroenPeterBos/notabene",
    download_url=(
        f"https://github.com/JeroenPeterBos/" f"notabene/archive/{version}.tar.gz"
    ),
    keywords=[
        # Add package keywords here.
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for.
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
)
