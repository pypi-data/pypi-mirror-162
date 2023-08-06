from setuptools import setup, find_packages

from calendric_lib import __version__


# Reading in README as text for description 
with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='calendric_lib',
    version=__version__,
    description = "Calendric-lib is a creative package for calendrical conversion operations in Python.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/saadbinmunir/Calendric-lib.git',
    author='Saad Bin Munir',
    author_email='saadmunir24@gmail.com',
    license='MIT',
    packages=find_packages(),
)
