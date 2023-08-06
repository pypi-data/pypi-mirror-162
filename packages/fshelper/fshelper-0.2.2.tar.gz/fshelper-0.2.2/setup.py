#!/usr/bin/env python

from setuptools import setup, find_packages  # type: ignore

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    author="Matthew Larsen",
    author_email="matt.larsen@connorgp.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="FreshService API usage helper",
    install_requires=["requests", ],
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_data={},
    include_package_data=True,
    keywords="fshelper",
    name="fshelper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    setup_requires=[],
    url="https://github.com/matt-larsen-sld/freshservice-helper",
    version="0.2.2",
    zip_safe=False,
)
