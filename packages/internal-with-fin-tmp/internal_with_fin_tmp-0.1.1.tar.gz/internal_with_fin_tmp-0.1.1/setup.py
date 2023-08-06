"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
from util import read_version
import shutil

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

version=read_version.get_version_from_file('VERSION')
public_version=read_version.get_version_from_file('PUBLIC_VERSION')
setup(
    install_requires=[
        "spark-nlp==4.0.0" #+ public_version
    ],
    name="internal_with_fin_tmp",  # Required
    version='0.1.1',##version,
    description="NLP Text processing library built on top of Apache Spark",
    long_description=long_description,
    url="http://nlp.johnsnowlabs.com",
    author="John Snow Labs",
    author_email="john@johnsnowlabs.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: Apache Software License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="NLP spark development",  # Optional
    packages=find_packages(exclude=["test_jsl"]),
    include_package_data=True,  # Needed to install jar file
)
