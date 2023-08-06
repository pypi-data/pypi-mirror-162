#! /usr/bin/env python3

# Packages
from setuptools import setup

setup(
    name="text-to-tweets",
    version="0.1.1",
    author="Robin Winslow",
    author_email="robin@robinwinslow.co.uk",
    url="https://github.com/nottrobin/text-to-tweets",
    description=(
        "Split a chunk of text into 280-character blocks"
        "Attempting to split at the end of sentences etc."
    ),
    packages=["text_to_tweets"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[]
)
