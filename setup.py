import sys

from setuptools import find_packages
from setuptools import setup


def runtests():
    sys.exit(0)


setup(
    name='swadl',
    version=0,
    author='akien',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='setup.runtests',
    install_requires=[
        'selenium',
    ],
)
