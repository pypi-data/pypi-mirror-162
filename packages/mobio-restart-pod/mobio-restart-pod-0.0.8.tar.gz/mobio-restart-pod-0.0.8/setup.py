#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
               ..
              ( '`<
               )(
        ( ----'  '.
        (         ;
         (_______,' 
    ~^~^~^~^~^~^~^~^~^~^~
    Author: ThongNV
    Company: M O B I O
    Date Created: 2/28/21
"""
import os
import pathlib

from setuptools import find_namespace_packages, setup


class Requirements(object):
    requirements_path = "requirements.txt"

    @staticmethod
    def get():
        """Retrieve all dependencies for this project
        :param filename:
        :return:
        """
        print(Requirements.requirements_path)
        print(os.path.exists(Requirements.requirements_path))
        print(os.getcwd())
        requirements = []

        return requirements


__PACKAGE_NAME__ = 'mobio-restart-pod'


def package_data_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        p = pathlib.Path(path)
        path = pathlib.Path(*p.parts[1:])
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths


with open("README.md", "r") as fh:
    long_description = fh.read()

data_files = package_data_files(__PACKAGE_NAME__)

version = "0.0.8"
setup(
    name="mobio-restart-pod",  # Required
    version=version,  # Required
    description="Restart pod kubernetes with kafka python",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/mobiovn",  # Optional
    author="Mobio",  # Optional
    author_email="contact@mobio-restart-pod.vn",  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="",  # Optional
    packages=find_namespace_packages(),  # Required
    package_data={'': data_files},
    python_requires=">=3",
    # install_requires=Requirements.get(),  # Optional
    project_urls={  # Optional
        # "Bug Reports": "https://github.com/mobiovn",
        # "Funding": "https://mobio.vn/",
        # "Say Thanks!": "https://mobio.vn/",
        # 'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        "Source": "https://github.com/mobiovn",
    },
    license="MIT",
)
