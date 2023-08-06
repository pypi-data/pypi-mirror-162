#! /usr/bin/env python3

# Packages
from setuptools import setup

setup(
    name="publish-markdown",
    version="0.1.0",
    author="Robin Winslow",
    author_email="robin@robinwinslow.co.uk",
    url="https://github.com/nottrobin/post-to-medium",
    description=(
        "For posting articles to Medium"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "requests>=2.28.1",
        "python-frontmatter>=1.0.0"
    ],
    scripts=["publish-to-medium"],
)
