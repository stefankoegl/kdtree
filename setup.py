#!/usr/bin/env python

from setuptools import setup
from setuptools.command.build_py import build_py
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

# Type stubs (PEP 484) for the modules. kdtree is a single-file module, so
# PEP 561's py.typed marker can not be used. Instead each stub is installed
# twice: next to its module (picked up by e.g. pyright and PyCharm) and as a
# stub-only package <module>-stubs (picked up by mypy). setuptools only
# installs .py files for py_modules, so the stubs are copied explicitly.
STUBS = {}
for module in MODULES:
    STUBS[module + '.pyi'] = module + '.pyi'
    STUBS[os.path.join(module + '-stubs', '__init__.pyi')] = module + '.pyi'


class build_py_with_stubs(build_py):
    """ build_py command that also installs the type stubs """

    def run(self):
        super().run()
        for target, source in STUBS.items():
            target = os.path.join(self.build_lib, target)
            self.mkpath(os.path.dirname(target))
            self.copy_file(os.path.join(dirname, source), target)

    def get_outputs(self, *args, **kwargs):
        outputs = super().get_outputs(*args, **kwargs)
        return outputs + [os.path.join(self.build_lib, t) for t in STUBS]


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
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Programming Language :: Python :: 3.13',
    'Programming Language :: Python :: 3.14',
    'Programming Language :: Python :: 3.15',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
    'Typing :: Typed',
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
      cmdclass={'build_py': build_py_with_stubs},
      download_url='http://pypi.python.org/packages/source/' + \
        PACKAGE[0] + '/' + PACKAGE + '/' + \
        PACKAGE + '-' + VERSION + '.tar.gz',
      classifiers=CLASSIFIERS,
      python_requires='>=3.11',
)
