#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 17:27:43 2022

@author: joern
"""

import pathlib
from setuptools import setup, find_packages


HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='cABCanalysis',
      python_requires='>=3.5',
      version='0.1.0',
      description='Nested computed ABC analysis (cABC): A method to reduce feature sets to their most relevant items. Implementation in Python.',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/JornLotsch/ABCanalysis',
      author='Jorn Lotsch',
      author_email='j.loetsch@em.uni-frankfurt.de',
      license='GNU General Public License v3 (GPLv3)',
      packages = find_packages(),
      zip_safe=False,
      install_requires=['numpy>=1.19.2',
                        'pandas>=1.1.5',
                        'seaborn>=0.11.2',
                        'scipy>=1.7.3'],
      keywords=['cABC analysis', 'ABC analysis', 'item categorization', 'feature selection', 'information reduction'],
      classifiers= [
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux"
        ])
