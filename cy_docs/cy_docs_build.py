import pathlib

from setuptools import setup
from Cython.Build import cythonize
import os
file=os.path.join(pathlib.Path(__file__).parent.__str__(), f"cy_docs_x.py")
print(file)
setup(
    name='cy_docs',
    ext_modules=cythonize(file),
    zip_safe=True,
)
"""
cd cy_docs
python cy_docs_build.py build_ext --inplace
"""
#python3 /home/vmadmin/python/v6/file-service-02/cy_docs/cy_docs_build.py build_ext --inplace