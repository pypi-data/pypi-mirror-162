# Copyright 2021 MosaicML. All Rights Reserved.

import os

import setuptools
from setuptools import setup


def package_files(prefix: str, directory: str, extension: str):
    # from https://stackoverflow.com/a/36693250
    paths = []
    for (path, _, filenames) in os.walk(os.path.join(prefix, directory)):
        for filename in filenames:
            if filename.endswith(extension):
                paths.append(os.path.relpath(os.path.join(path, filename), prefix))
    return paths


data_files = package_files("mcontrib", "algorithms", ".json")

install_requires = [
    "mosaicml>=0.8.0",
]

extra_deps = {
    'dev': [
        "pytest==7.1.0",
        "toml==0.10.2",
        "yapf==0.32.0",
        "isort==5.10.1",
        "yamllint==1.26.3",
    ]
}

setup(
    name="mcontrib",
    version="0.0.2",
    author="MosaicML",
    author_email="team@mosaicml.com",
    description="mosaicml contrib of third-party algorithms",
    url="https://github.com/mosaicml/mcontrib",
    include_package_data=True,
    package_data={
        "mcontrib": data_files,
    },
    packages=setuptools.find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=install_requires,
    extras_require=extra_deps,
    python_requires=">=3.7",
)
