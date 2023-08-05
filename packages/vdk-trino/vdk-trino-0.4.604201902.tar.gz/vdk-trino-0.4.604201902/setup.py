# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import setuptools


__version__ = "0.4.604201902"

setuptools.setup(
    name="vdk-trino",
    version=__version__,
    url="https://github.com/vmware/versatile-data-kit",
    description="Versatile Data Kit SDK plugin provides support for trino database and trino transformation templates.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=["vdk-core", "vdk-lineage-model", "trino", "tabulate", "sqlparse"],
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    entry_points={"vdk.plugin.run": ["vdk-trino = vdk.plugin.trino.trino_plugin"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
