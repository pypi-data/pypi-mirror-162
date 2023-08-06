#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="relations-sqlite",
    version="0.6.1",
    package_dir = {'': 'lib'},
    py_modules = [
        'relations_sqlite',
        'relations_sqlite.sql',
        'relations_sqlite.expression',
        'relations_sqlite.criterion',
        'relations_sqlite.criteria',
        'relations_sqlite.clause',
        'relations_sqlite.query',
        'relations_sqlite.ddl',
        'relations_sqlite.column',
        'relations_sqlite.index',
        'relations_sqlite.table'
    ],
    install_requires=[
        'relations-sql>=0.6.6'
    ],
    url="https://github.com/relations-dil/python-relations-sqlite",
    author="Gaffer Fitch",
    author_email="relations@gaf3.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=('LICENSE.txt',),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ]
)
