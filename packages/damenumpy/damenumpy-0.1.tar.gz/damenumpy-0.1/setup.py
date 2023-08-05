#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gmail.com>
# Maintainer: David Arroyo Menéndez <davidam@gmail.com>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with DameNumpy; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from setuptools import setup
from os import path

# def readme():
#     with open('README.org') as f:
#         return f.read()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='damenumpy',
      version='0.1',
      description='Learning Numpy from Tests by David Arroyo Menéndez',
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
      ],
      keywords='numpy tests',
      scripts=['damenumpy/bin/damenumpy-sum.py'],
      url='http://github.com/davidam/damenumpy',
      author='David Arroyo Menéndez',
      author_email='davidam@gmail.com',
      license='GPLv3',
      packages=['damenumpy', 'damenumpy.tests'],
      package_dir={'damenumpy': 'damenumpy',
                   'damenumpy.tests': 'damenumpy/tests',
                   'damenumpy.bin': 'damenumpy/bin'},
      install_requires=[
          'markdown',
          'numpy',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      include_package_data=True,
      zip_safe=False)
