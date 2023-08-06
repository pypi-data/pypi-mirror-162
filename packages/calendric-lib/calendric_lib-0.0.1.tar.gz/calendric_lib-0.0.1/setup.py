from setuptools import setup, find_packages

from calendric_lib import __version__

setup(
    name='calendric_lib',
    version=__version__,

    url='https://github.com/saadbinmunir/Calendric-lib.git',
    author='Saad Bin Munir',
    author_email='saadmunir24@gmail.com',

    packages=find_packages(),
)
