#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


with open("README.md") as readme_file:
    readme = readme_file.read()


with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "threedi-api-client>=3.0.24",
    "PyYAML>=5.1",
    "websockets>=8.1",
    "arrow>=0.14.4",
    "Jinja2>=2.10.1",
    "slackclient>=2.8.2",
    "click>=7.1.2",
    "requests>=2.25.0",
    "rich>=9.4.0",
    "typer>=0.3.2",
]

setup_requirements = [
    "pip>=20.3.3",
    "wheel>=0.33.6",
    "flake8>=3.7.8",
    "tox>=3.14.0",
    "coverage>=4.5.4",
    "twine>=1.14.0",
    "black>=20.8b1",
]


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


test_requirements = []

main_entry_points = [
    "scenarios=threedi_cmd.commands.scenarios:scenario_app",
    "suite=threedi_cmd.commands.suite:suite_app",
    "live=threedi_cmd.commands.active_simulations:active_sims_app",
    "api=threedi_cmd.commands.api:api_app",
    "3Di_cmd=threedi_cmd.commands.main:app",
]

setup(
    author="Jelle Prins",
    author_email="info@nelen-schuurmans.nl",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
    description="Python 3Di command line client",
    long_description_content_type="text/markdown",
    long_description=readme + "\n\n" + history,
    install_requires=requirements,
    license="MIT license",
    entry_points={"console_scripts": main_entry_points},
    include_package_data=True,
    keywords="3Di, client, command line, scenario",
    name="threedi_cmd",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
        include=["threedi_cmd", "threedi_cmd.*"],
    ),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/nens/threedi-cmd",
    version=find_version("threedi_cmd", "version.py"),
    zip_safe=False,
)
