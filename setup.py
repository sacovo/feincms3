#!/usr/bin/env python3

import os
from io import open

from setuptools import find_packages, setup


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


setup(
    name="feincms3",
    version=__import__("feincms3").__version__,
    description="CMS-building toolkit for Django",
    long_description=read("README.rst"),
    author="Matthias Kestenholz",
    author_email="mk@feinheit.ch",
    url="https://github.com/matthiask/feincms3/",
    license="BSD License",
    platforms=["OS Independent"],
    packages=find_packages(exclude=["tests", "testapp"]),
    include_package_data=True,
    install_requires=["django-content-editor", "django-tree-queries>=0.4.1"],
    python_requires=">=3.6",
    extras_require={
        "all": [
            "django-ckeditor",
            "django-imagefield",
            "html-sanitizer>=1.1.1",
            "requests",
        ],
        "versatileimagefield": [
            "django-ckeditor",
            "django-versatileimagefield",
            "html-sanitizer>=1.1.1",
            "requests",
        ],
    },
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    zip_safe=False,
)
