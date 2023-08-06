from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("src",  ["src/test.py"]),
#   ... all your modules that need be compiled ...
]
setup(
    name = 'fastcython',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    zip_safe=False,
)