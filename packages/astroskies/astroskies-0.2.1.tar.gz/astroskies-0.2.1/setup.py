# -*- coding: utf-8 -*-
from setuptools import setup

description = "Demo project to learn Django Dockerization"

setup(
    name="astroskies",
    version="0.2.1",
    author="Urtzi Odriozola",
    author_email="uodriozola@codesyntax.com",
    packages=["astroskies"],
    url="https://github.com/urtzai/astroskies",
    license="MIT",
    description=description,
    long_description=open("README.rst").read(),
    zip_safe=False,
    include_package_data=True,
    package_data={"": ["README.rst"]},
    install_requires=[
        "Django==4.1",
        "django-user-agents",
        "mysqlclient",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
