from datetime import datetime, timezone
from setuptools import find_packages
from setuptools import setup
import os
import sys


def runtests():
    sys.exit(0)


# We'll need these
user_name = os.environ.get('USERNAME')
# Set unique version number
VERSION = f"{datetime.now(timezone.utc).strftime('%Y%m%d.%H%M%S.%f')[:-2]}"  # .{user_name}"

setup(
    name='swadl',
    version=VERSION,
    author=os.environ.get('USERNAME'),
    packages=find_packages(),
    package_dir={"": "."},
    include_package_data=True,
    package_data={"mypkg": ["*.json"]},
    zip_safe=False,
    test_suite='setup.runtests',
    install_requires=open('requirements.txt').read().splitlines(),
)
