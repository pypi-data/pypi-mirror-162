#!/usr/bin/python
# coding=utf-8

from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='wwprocess',
    version='0.0.10',
    description=(
        'for processing windworks'
    ),
    long_description=Path('README.md').read_text(encoding='utf8'),
    author='jiang yuanji',
    author_email='jiangyuanji@126.com',
    maintainer='jiang yuanji',
    maintainer_email='jiangyuanji@126.com',
    license='GNU License',
    packages=find_packages(exclude=['tests']), # 列表中传入不查找的目录
    platforms=["all"],
    # url='<项目的网址，我一般都是github的url>',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'matplotlib>=3.5.2',
        'numpy>=1.21.6'
    ]
)
