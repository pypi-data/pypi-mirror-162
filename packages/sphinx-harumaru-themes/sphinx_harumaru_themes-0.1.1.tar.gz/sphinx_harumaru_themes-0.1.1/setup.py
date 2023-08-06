# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.rst") as f:
    readme = f.read()

setup(
    name="sphinx_harumaru_themes",
    version="0.1.1",
    author="DanielSDVG",
    author_email="danielsdvg@gmail.com",
    url="",
    description="A package with cute Sphinx documentation themes",
    long_description=readme,
    license="MIT",
    packages=["sphinx_harumaru_themes"],
    package_data={
        "sphinx_harumaru_themes": [
            "haruki_hw_theme/*",
            "haruki_hw_theme/static/*",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "sphinx.html_themes": [
            "haruki_hw = sphinx_harumaru_themes",
        ]
    },
)