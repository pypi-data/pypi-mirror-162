from setuptools import setup, find_packages
import codecs
import os
import pathlib

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

VERSION = '1.1.1'
DESCRIPTION = ' A Topsis package developed by BHAGWAN BANSAL'
# Setting up
setup(
    name="BhagwanTopsis",
    version=VERSION,
    author="Bhagwan Bansal",
    author_email="<bansalbhagwan5@gmail.com>",
    description=DESCRIPTION,
    long_description=README,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)