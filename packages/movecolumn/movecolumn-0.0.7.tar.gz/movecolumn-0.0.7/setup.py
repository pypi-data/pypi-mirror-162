from setuptools import setup, find_packages
from movecolumn import __version__


# Reading in README as text for description 
with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()


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
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/saadbinmunir/MoveColumn',
    author='Saad Bin Munir',
    author_email='saadmunir24@gmail.com',
    license='Apache License 2.0',
    classifiers= CLASSIFIERS,
    packages=find_packages(),
)