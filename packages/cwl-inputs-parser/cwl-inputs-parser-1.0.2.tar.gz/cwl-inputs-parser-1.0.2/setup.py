#!/usr/bin/env python3
# coding: utf-8
from pathlib import Path

from setuptools import setup

long_description = Path(__file__).parent.joinpath("README.md").read_text(encoding="utf-8")  # noqa: E501

setup(
    name="cwl-inputs-parser",
    version="1.0.2",
    license="Apache 2.0",
    description="The parser of inputs field in Common Workflow Language (CWL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="suecharo",
    author_email="suehiro619@gmail.com",
    url="https://github.com/suecharo/cwl-inputs-parser",
    python_requires=">=3.6",
    install_requires=[
        "cwl-utils",
        "flask",
        "pyyaml",
        "requests",
        "cwltool",
        "ruamel.yaml",
    ],
    extras_require={
        "testing": [
            "flake8",
            "isort",
            "jsonschema",
            "mypy",
            "pytest",
            "types-PyYAML",
            "types-requests",
            "types-setuptools",
        ],
    },
    packages=["cwl_inputs_parser"],
    entry_points={
        "console_scripts": [
            "cwl-inputs-parser=cwl_inputs_parser.main:main",
        ]
    },
    data_files=[
        (".", ["LICENSE", "README.md", "cwl-inputs-parser-schema.json"]),
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
