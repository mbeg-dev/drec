from setuptools import Extension, setup
from Cython.Build import cythonize

extensions = [Extension("iec61850",
                        ["iec61850_client.pyx"],
                        include_dirs=["src/include"],
                        extra_objects=["src/lib/libiec61850.a"])]

setup(
    name = 'iec61850',
    version = '0.0.1',
    description='Wrapper for libIEC61850 C library - disturbance record download only via MMS file transfer',
    author = 'Marko Begović',
    license = 'GPLv3',
    license_files = ('LICENSE.txt',),
    platforms=['linux'],
    ext_modules = cythonize(extensions, language_level = '3')
)
