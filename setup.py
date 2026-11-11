""" Installs the type stubs along with the module

All metadata is in pyproject.toml. This file only exists because
setuptools has no declarative way to install the stubs: kdtree is a
single-file module, so PEP 561's py.typed marker can not be used. Instead
each stub is installed twice: next to its module (picked up by e.g. pyright
and PyCharm) and as a stub-only package <module>-stubs (picked up by mypy).
setuptools only installs .py files for py-modules, so the stubs are copied
explicitly. """

import os.path

from setuptools import setup
from setuptools.command.build_py import build_py

dirname = os.path.dirname(os.path.abspath(__file__))

MODULES = ('kdtree',)

# {installed path: source path}
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


setup(cmdclass={'build_py': build_py_with_stubs})
