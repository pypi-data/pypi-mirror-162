#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Rayson.Shi
# Mail: raysonshi@qq.com
# Created Time:  2022-8-5 23:17:34
#############################################
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cocoutils-cv",
    version="0.0.1",
    description=("Microsoft COCO data set transformation analysis utils"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RaysonShi",
    author_email="raysonshi@qq.com",
    url="https://github.com/Rayson2020-8/cocodataset-utils",
    license="MIT Licence",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pycocotools',
        'matplotlib',
        'tqdm',
        'opencv-python',
    ],
    classifiers=[
                  "Programming Language :: Python :: 3",
                  "License :: OSI Approved :: MIT License",
                  "Operating System :: OS Independent",
              ]
)
