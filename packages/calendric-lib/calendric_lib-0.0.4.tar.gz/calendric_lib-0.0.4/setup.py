from setuptools import setup, find_packages

from calendric_lib import __version__

import pypandoc 

setup(
    name='calendric_lib',
    version=__version__,
    description = "Calendric-lib is a creative package for calendrical conversion operations in Python.",
    long_description="""# Calendric-lib

[![GitHub issues](https://img.shields.io/github/issues/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/issues)
[![GitHub forks](https://img.shields.io/github/forks/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/network)
[![GitHub stars](https://img.shields.io/github/stars/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/stargazers)
[![GitHub license](https://img.shields.io/github/license/saadbinmunir/Calendric-lib)](https://github.com/saadbinmunir/Calendric-lib/blob/main/LICENSE)

#  About
Calendric-lib is a creative package for calendrical conversion operations in Python.

""",
    long_description_content_type='text/markdown',
    url='https://github.com/saadbinmunir/Calendric-lib.git',
    author='Saad Bin Munir',
    author_email='saadmunir24@gmail.com',

    packages=find_packages(),
)
