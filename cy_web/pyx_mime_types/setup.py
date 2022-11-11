import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()

file_pyx_mime_types=os.path.join(build_dir, f"pyx_mime_types.py")

setup(
    name='pyx_mime_types_x',
    ext_modules=cythonize(file_pyx_mime_types),
    zip_safe=True,
)

"""
cd cy_web/source
python cy_web/pyx_mime_types/setup.py build_ext --inplace
"""