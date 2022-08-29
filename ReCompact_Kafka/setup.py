from setuptools import setup
from Cython.Build import cythonize
import pathlib
import os
dir_path = str(pathlib.Path(__file__).parent)
setup(
    name = "ReCompact_Kafka",
    ext_modules = cythonize(os.path.join(dir_path,"__init__.py"))
)
"""
python setup.py build_ext --inplace
python setup.py install

"""