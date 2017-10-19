#!/usr/bin/env python

from setuptools import setup
import re
import os.path

dirname = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(dirname, 'kdtree.py')
src = open(filename).read()
metadata = dict(re.findall("__([a-z]+)__ = u?'([^']+)'", src))
docstrings = re.findall('"""([^"]+)"""', src)

PACKAGE = 'kdtree'

MODULES = (
        PACKAGE,
)

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
WEBSITE = metadata['website']
LICENSE = metadata['license']
DESCRIPTION = docstrings[0].strip()
if '\n\n' in DESCRIPTION:
    DESCRIPTION, LONG_DESCRIPTION = DESCRIPTION.split('\n\n', 1)
else:
    LONG_DESCRIPTION = None

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: ISC License (ISCL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]


setup(name=PACKAGE,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=WEBSITE,
      py_modules=MODULES,
      download_url='http://pypi.python.org/packages/source/' + \
        PACKAGE[0] + '/' + PACKAGE + '/' + \
        PACKAGE + '-' + VERSION + '.tar.gz',
      classifiers=CLASSIFIERS,
      test_suite='test',
)
