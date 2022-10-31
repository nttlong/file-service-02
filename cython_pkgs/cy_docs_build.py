import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
file=os.path.join(pathlib.Path(__file__).parent.__str__(),"cy_docs",f"cy_docs.py")
print(file)
setup(
    name='cy_docs',
    ext_modules=cythonize(file),
    zip_safe=True,
)
"""
cd cython_pkgs
python cython_pkgs/cy_docs_build.py build_ext --inplace
"""