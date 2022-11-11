import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()

file_pyx_re_quicky_routers=os.path.join(build_dir, f"pyx_re_quicky_routers.py")


setup(
    name='pyx_re_quicky_routers',
    ext_modules=cythonize(file_pyx_re_quicky_routers),
    zip_safe=True,
)
#python3 cy_web/re_quicky_routers/setup.py build_ext --inplace