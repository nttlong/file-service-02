import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
build_dir = pathlib.Path(__file__).parent.__str__()
file_pyx_re_quicky=os.path.join(build_dir, f"pyx_re_quicky.py")
file_pyx_re_quicky_routers=os.path.join(build_dir, f"pyx_re_quicky_routers.py")
file_pyx_mime_types=os.path.join(build_dir, f"pyx_mime_types.py")
print(file_pyx_re_quicky)
setup(
    name='re_quicky_x',
    ext_modules=cythonize(file_pyx_re_quicky),
    zip_safe=True,
)
#python3 cy_web/pyx_re_quicky/setup.py build_ext --inplace