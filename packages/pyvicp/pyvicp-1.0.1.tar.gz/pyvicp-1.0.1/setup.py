#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

if __name__ == "__main__":
    setup(
        name="pyvicp",
        packages=["pyvicp"],
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
    )
