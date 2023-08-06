#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, Extension
import os


with open('README.md', "r") as file:
    long_description = file.read()


setup(
    name='xcache-lib',
    version='0.0.2',
    description='A simplest and thread-safe LRU cache, which support key-func, release-func and hit-stat.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Chuanqi Tan',
    author_email='chuanqi.tan@gmail.com',
    url='https://github.com/ChuanqiTan/xcache',
    license='MIT',
    keywords='thread safe cache, LRU cache, key function, release function, hit stat',
    packages=[
        'xcache',
    ],
    install_requires=[
    ],
)
