from setuptools import setup, find_packages
from movecolumn import __version__

CLASSIFIERS = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
          #  "License :: OSI Approved :: Apache Licence 2.0",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development",
            "Topic :: Scientific/Engineering",
            "Typing :: Typed",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
                ]

setup(
    name='movecolumn',
    version=__version__,
    description = "A creative package to move columns in Python dataframes.",
    long_description = '' ,
    url='https://github.com/saadbinmunir/Calendric-lib.git',
    author='Saad Bin Munir',
    author_email='saadmunir24@gmail.com',
    license='Apache License 2.0',
    classifiers= CLASSIFIERS,
    packages=find_packages(),
)