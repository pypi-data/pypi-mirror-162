# -*- coding: utf-8 -*-
# @Time    : 9/16/2021 9:53 AM
# @Author  : Joseph Chen
# @Email   : josephchenhk@gmail.com
# @FileName: setup.py
# @Software: PyCharm

"""
Copyright (C) 2020 Joseph Chen - All Rights Reserved
You may use, distribute and modify this code under the
terms of the JXW license, which unfortunately won't be
written for another century.

You should have received a copy of the JXW license with
this file. If not, please write to: josephchenhk@gmail.com
"""

from distutils.core import setup
from Cython.Build import cythonize

"""
Usage:

> python setup.py build_ext --inplace
"""

setup(
    name='Engines',
    ext_modules=cythonize(
        ["event_engine.py",
         "engine.py"]
    ),
)
