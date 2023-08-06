#! /usr/bin/env python3

# Packages
from setuptools import setup

setup(
    name="publish-markdown",
    version="0.2.1",
    author="Robin Winslow",
    author_email="robin@robinwinslow.co.uk",
    url="https://github.com/nottrobin/publish-markdown",
    description=(
        "Publish articles written in Markdown files "
        "to medium.com, dev.to, hashnode and twitter"
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["publish_markdown"],
    install_requires=[
        "requests>=2.28.1",
        "python-frontmatter>=1.0.0"
    ],
    scripts=[
        "publish-to-medium",
        "publish-to-DEV"
    ],
)
