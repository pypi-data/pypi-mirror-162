# -*- coding: utf-8 -
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'grid5000', '__version__.py')) as f:
    exec(f.read(), about)

setup(version=about["__version__"])

