import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
file_pyx_re_quicky=os.path.join(pathlib.Path(__file__).parent.__str__(), f"pyx_re_quicky.py")
file_pyx_re_quicky_routers=os.path.join(pathlib.Path(__file__).parent.__str__(), f"pyx_re_quicky_routers.py")
print(file_pyx_re_quicky)
setup(
    name='re_quicky_x',
    ext_modules=cythonize(file_pyx_re_quicky),
    zip_safe=True,
)
setup(
    name="",
    ext_modules=cythonize(file_pyx_re_quicky_routers),
    zip_safe=True,
)
"""
cd re_quicky/source
python setup.py build_ext --inplace
"""