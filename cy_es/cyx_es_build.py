import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()
file_cyx_es=os.path.join(build_dir, f"cyx_es.py")

setup(
    name='pyx_re_quicky_routers_x',
    ext_modules=cythonize(file_cyx_es),
    zip_safe=True,
)

"""
cd cy_es
python cyx_es_build.py build_ext --inplace
"""