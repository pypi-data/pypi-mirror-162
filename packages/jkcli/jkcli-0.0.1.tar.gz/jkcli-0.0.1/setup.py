import os
import setuptools
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from jkcli.version import __prog__, __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=__prog__,
    version=__version__,
    author="Luan Tran",
    author_email="minhluantran017@gmail.com",
    description="Small tool to interactive with Jenkins through commandline interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minhluantran017/jkcli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)