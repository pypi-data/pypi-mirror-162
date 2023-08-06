# -*- coding: utf-8 -*-
import setuptools
from sys import version_info
from os.path import dirname, join

if version_info < (3, 8, 0):
    raise SystemExit("Sorry! hasaki requires python 3.8.0 or later.")

with open(join(dirname(__file__), "hasaki/VERSION"), "rb") as fh:
    version = fh.read().decode("ascii").strip()

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = setuptools.find_packages()

install_requires = [
    "redis>=4.3.4",
]

extras_requires = ["PyExecJS>=1.5.1"]

setuptools.setup(
    name="hasaki",
    version=version,
    author="BishopMarcel",
    license="MIT",
    author_email="bishopmarcel@163.com",
    python_requires=">=3.8",
    description="hasaki是一个python3开发常用工具的包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    extras_require={"all": extras_requires},
    url="https://github.com/BishopMarcel/hasaki.git",
    packages=packages,
    classifiers=["Programming Language :: Python :: 3"],
)
