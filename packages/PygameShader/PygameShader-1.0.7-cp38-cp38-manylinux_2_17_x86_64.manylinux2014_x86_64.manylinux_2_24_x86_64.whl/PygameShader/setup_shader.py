# encoding: utf-8
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

from Cython.Build import cythonize

from distutils.core import setup
from distutils.extension import Extension

import numpy

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# /O2 sets a combination of optimizations that optimizes code for maximum speed.
# /Ot (a default setting) tells the compiler to favor optimizations for speed over
# optimizations for size.
# /Oy suppresses the creation of frame pointers on the call stack for quicker function calls.
setup(
    name='SHADER',
    ext_modules=cythonize([
        Extension("shader", ["shader.pyx"],
                  extra_compile_args=["-DPLATFORM=linux", "-march=x86-64", "-m64",  "-O3", "-Wall", "-lgomp"],
                  # -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing
                  language="c"),
        Extension("misc", ["misc.pyx"],
                  extra_compile_args=["-DPLATFORM=linux", "-march=x86-64", "-m64",  "-O3", "-Wall", "-lgomp"],
                  language="c"),
        Extension("gaussianBlur5x5", ["gaussianBlur5x5.pyx"],
                  extra_compile_args=["-DPLATFORM=linux", "-march=x86-64", "-m64",  "-O3", "-Wall", "-lgomp"],
                  language="c"),
        Extension("Palette", ["Palette.pyx"],
                  extra_compile_args=["-DPLATFORM=linux", "-march=x86-64", "-m64",  "-O3", "-Wall", "-lgomp"],
                  language="c"),
        Extension("shader_gpu", ["shader_gpu.pyx"],
                  extra_compile_args=["-DPLATFORM=linux", "-march=x86-64", "-m64",  "-O3", "-Wall", "-lgomp"],
                  language="c"),

    ]),


    include_dirs=[numpy.get_include(), '../Include'],

)
