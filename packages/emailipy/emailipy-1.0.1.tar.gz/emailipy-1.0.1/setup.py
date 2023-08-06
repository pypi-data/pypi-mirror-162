import sys

from setuptools import setup, find_packages


setup(
    name="emailipy",
    packages=find_packages(),
    version="1.0.1",
    url="https://github.com/Parsely/emailipy",
    description="Inlines css into html to make it safe for email.",
    install_requires=[
        "beautifulsoup4", # required for lxml.html.soupparser
        "click",
        "cssselect",
        "lxml",
        "tinycss",
    ],
    entry_points={
        "console_scripts": [
            "emailipy-lint = emailipy.cli:lint",
            "emailipy-inline = emailipy.cli:inline",
        ]
    },
)
