#!/usr/bin/env python3

import setuptools
import x9k3

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="x9k3",
    version=x9k3.version(),
    author="Adrian",
    author_email="spam@iodisco.com",
    description="HLS Segmenter with SCTE-35 Support",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/futzu/x9k3",
    packages=setuptools.find_packages(),
    install_requires=[
          'threefive',
      ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.6",
)
