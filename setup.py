#!/usr/bin/env python
from itertools import chain

from setuptools import find_packages, setup

from msal_requests_auth import __version__

requirements = ["msal", "requests", "pyperclip"]
extras_require = {"dev": ["pytest", "pytest-cov"]}
extras_require["all"] = list(chain.from_iterable(extras_require.values()))

setup(
    install_requires=requirements,
    extras_require=extras_require,
    packages=find_packages(include=["msal_requests_auth*"]),
    version=__version__,
)
