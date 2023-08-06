#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_namespace_packages

setup(
    name="federhmaccard",
    version="1.0",
    packages=find_namespace_packages(
        where=".",
        exclude=["zccard"],
    ),
    install_requires=[
        'pyperclip',
        'pyscard',
    ],
)
