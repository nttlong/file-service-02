import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()
file_cy_kit_x=os.path.join(build_dir, f"cy_kit_x.py")

setup(
    name='pyx_re_quicky_routers_x',
    ext_modules=cythonize(file_cy_kit_x),
    zip_safe=True,
)

"""
cd cy_kit
python cy_kit/setup.py build_ext --inplace
"""