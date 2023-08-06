"""Setup file for distribution artifacts."""

from __future__ import print_function

import pathlib
from os import path
import sys

from setuptools import setup

(major, minor) = (sys.version_info.major, sys.version_info.minor)
if major != 3 or minor < 6:
    print('Send.lk requires python >= 3.6', file=sys.stderr)
    sys.exit(1)

about_path = path.join(path.dirname(path.abspath(__file__)), 'sendlk', '__about__.py')
readme_path = path.join(path.dirname(path.abspath(__file__)), 'README.md')
about = {}
with open(about_path) as fp:
    exec(fp.read(), about)

long_description = ""
long_description = pathlib.Path(readme_path).read_text()
__version__ = about['__version__']
__title__ = about['__title__']
__url__ = about['__url__']
__author__ = about['__author__']
__author_email__ = about['__author_email__']
__license__ = about['__license__']


install_requires = [
    'requests>=2.26.0',
    'cryptography>=36.0.1'
]

setup(
    name=__title__,
    version=__version__,
    description='Send.lk Python SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    keywords='send.lk sms getaway',
    install_requires=install_requires,
    packages=['sendlk'],
    download_url=f'https://github.com/ishangavidusha/sendlk-sdk-python/archive/refs/tags/v{__version__}.tar.gz',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
)

