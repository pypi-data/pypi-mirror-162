#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    reshapedata LLC
"""
import platform
from setuptools import setup
from setuptools import find_packages

setup(
    name  ='pyzz123',
    version = '1.0.0',
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    license = 'Apache License',
    author = 'zhangzhi',#要在公司注册
    author_email = '1642699718@qq.com',#公司的邮箱
    url = 'http://www.reshapedata.com',#公司的url
    description = 'reshape data type in py language ',
    keywords = ['reshapedata', 'rdt','pyrdt'],
    python_requires='>=3.6',
)
