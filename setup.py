#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import dirname, realpath, exists
from setuptools import setup
import sys


author = u"Paul Müller"
authors = [author, u"Philipp Rosendahl", u"Maik Herbig"]
name = 'shapeout'
description = 'Data analysis for real-time deformability cytometry (RTDC)'
year = "2015"

long_description = """
This package provides a graphical user interface for the analysis of
cytometry data generated by the RTDC setup of ZellMechanik Dresden.
"""

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
try:
    from _version import version
except:
    version = "unknown"



if __name__ == "__main__":
    setup(
        name=name,
        author=author,
        author_email='paul.mueller at biotec.tu-dresden.de',
        url='https://github.com/ZellMechanik-Dresden/ShapeOut',
        version=version,
        packages=[name],
        package_dir={name: name},
        license="GPL v2",
        description=description,
        long_description=open('README.rst').read() if exists('README.rst') else '',
        extras_require = {
            # If you need the GUI of this project in your project, add
            # "thisproject[GUI]" to your install_requires
            # Graphical User Interface
            'GUI':  ["wxPython", "chaco", "opencv"],
            # kiwisolver?
        },
        install_requires=["dclab", "NumPy>=1.7.0", "SciPy>=0.10.0",
                          "pyper"],
        setup_requires=['pytest-runner'],
        tests_require=["pytest"],
        keywords=["RTDC", "cytometry"],
        classifiers= [
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Intended Audience :: Science/Research'
                     ],
        platforms=['ALL']
        )
