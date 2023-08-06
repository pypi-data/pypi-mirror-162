"""ACTS Core is the Core Backend Python Library for Project ACTS."""

from __future__ import annotations

import setuptools
import os


PACKAGE_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DOCLINES = __doc__.split("\n")


def get_requirements() -> list[str]:
    with open("requirements/base.txt", "r") as fp:
        package_list = fp.readlines()
        package_list = [package.rstrip() for package in package_list]

    return package_list


def get_version() -> str:
    version = {}
    version_file = os.path.join(
        PACKAGE_ROOT_DIR,
        "acts",
        "core",
        "version.py",
    )
    with open(os.path.join(version_file)) as fp:
        exec(fp.read(), version)

    return version["__version__"]


setuptools.setup(
    name="acts.core",
    description=DOCLINES[0],
    author="Project ACTS - Software Development Team",
    version=get_version(),
    install_requires=get_requirements(),
    include_package_data=True,
    packages=setuptools.find_namespace_packages(
        include=[
            "acts.*",
        ]
    ),
    python_requires=">=3.7",
)
