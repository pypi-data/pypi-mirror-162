# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : 小易
# @File : setup.py.py
# @Project : webuitestpythonProject

from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(name='UI_Test_Project',  # 包名
      version='1.0.1',  # 版本号
      description='A small uitestproject example package',
      long_description=long_description,
      author='yc_talk',
      author_email='1284560817@qq.com',
      url='https://github.com/cxyyicheng',
      install_requires=[],
      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )
