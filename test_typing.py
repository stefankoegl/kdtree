#!/usr/bin/env python

""" Tests for the type stubs in kdtree.pyi

The tests that only need the standard library always run. The tests that
need mypy, pyright or setuptools are skipped if those are not installed. """

import ast
import importlib.util
import inspect
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import kdtree
import typing_sample


HERE = os.path.dirname(os.path.abspath(__file__))
STUB = os.path.join(HERE, 'kdtree.pyi')
SAMPLE = os.path.join(HERE, 'typing_sample.py')


def has_module(name):
    return importlib.util.find_spec(name) is not None


def parse_stub():
    """ Returns {name: ast node} for the public top-level stub definitions,
    and {class name: {member name: ast node}} for the stub's classes """

    with open(STUB) as f:
        tree = ast.parse(f.read(), STUB)

    toplevel = {}
    classes = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            toplevel[node.name] = node
        elif isinstance(node, ast.AnnAssign):
            toplevel[node.target.id] = node

        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                n.name: n for n in node.body if isinstance(n, ast.FunctionDef)
            }

    return toplevel, classes


def stub_params(func):
    """ Returns the (name, has_default) parameters of a stub function

    Overloaded functions are merged: a parameter has a default if it has one
    in any overload. """

    args = func.args
    positional = args.posonlyargs + args.args
    defaults = [False] * (len(positional) - len(args.defaults)) + \
               [True] * len(args.defaults)
    params = list(zip([a.arg for a in positional], defaults))
    params += [(a.arg, d is not None)
               for a, d in zip(args.kwonlyargs, args.kw_defaults)]
    return params


def stub_signatures(nodes):
    """ Merge the parameters of all (overloaded) definitions of a function """

    merged = {}
    order = []
    for node in nodes:
        for name, has_default in stub_params(node):
            if name not in merged:
                order.append(name)
                merged[name] = has_default
            merged[name] = merged[name] or has_default
    return [(name, merged[name]) for name in order]


def runtime_params(func):
    sig = inspect.signature(func)
    return [(p.name, p.default is not inspect.Parameter.empty)
            for p in sig.parameters.values()]


def public_runtime_names():
    """ Returns the public names defined in kdtree.py itself """

    names = set()
    for name, obj in vars(kdtree).items():
        if name.startswith('_'):
            continue
        if getattr(obj, '__module__', None) == 'kdtree':
            names.add(name)
    return names


class StubConsistencyTests(unittest.TestCase):
    """ Checks that the stub matches kdtree.py, using only the stdlib """

    def setUp(self):
        self.toplevel, self.classes = parse_stub()

    def all_stub_defs(self, name, members=None):
        """ All (possibly overloaded) definitions of a name in the stub """
        with open(STUB) as f:
            tree = ast.parse(f.read(), STUB)

        body = tree.body
        if members is not None:
            body = next(n.body for n in body
                        if isinstance(n, ast.ClassDef) and n.name == members)

        return [n for n in body
                if isinstance(n, ast.FunctionDef) and n.name == name]

    def test_public_names_in_stub(self):
        """ every public name of kdtree.py is declared in the stub """
        missing = public_runtime_names() - set(self.toplevel)
        self.assertEqual(missing, set())

    def test_metadata_in_stub(self):
        for name in ('__author__', '__version__', '__website__',
                     '__license__'):
            self.assertIn(name, self.toplevel)
            self.assertIsInstance(getattr(kdtree, name), str)

    def test_no_extra_public_names_in_stub(self):
        """ the stub does not declare public names that do not exist """
        stub_public = {n for n in self.toplevel if not n.startswith('_')}
        extra = {n for n in stub_public if not hasattr(kdtree, n)}
        self.assertEqual(extra, set())

    def test_function_signatures(self):
        for name in public_runtime_names():
            func = getattr(kdtree, name)
            if inspect.isclass(func):
                continue

            with self.subTest(function=name):
                expected = runtime_params(func)
                actual = stub_signatures(self.all_stub_defs(name))
                self.assertEqual(actual, expected)

    def test_method_signatures(self):
        for cls_name in ('Node', 'KDNode'):
            cls = getattr(kdtree, cls_name)
            stub_members = self.classes[cls_name]

            for name, member in vars(cls).items():
                if name.startswith('_') and name != '__init__':
                    continue

                with self.subTest(cls=cls_name, member=name):
                    self.assertIn(name, stub_members)

                    if isinstance(member, property):
                        continue

                    func = inspect.unwrap(member)
                    expected = runtime_params(func)
                    actual = stub_signatures(
                        self.all_stub_defs(name, members=cls_name))
                    self.assertEqual(actual, expected)

    def test_properties(self):
        """ properties at runtime are properties in the stub """
        for cls_name in ('Node', 'KDNode'):
            cls = getattr(kdtree, cls_name)
            for name, member in vars(cls).items():
                if not isinstance(member, property):
                    continue

                with self.subTest(cls=cls_name, member=name):
                    node = self.classes[cls_name][name]
                    decorators = [ast.unparse(d) for d in node.decorator_list]
                    self.assertIn('property', decorators)

    def test_instance_attributes(self):
        """ attributes set in __init__ are declared in the stub """
        with open(STUB) as f:
            tree = ast.parse(f.read(), STUB)

        declared = {}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                declared[node.name] = {
                    n.target.id for n in node.body
                    if isinstance(n, ast.AnnAssign)
                }

        node_attrs = set(vars(kdtree.Node()))
        kdnode_attrs = set(vars(kdtree.KDNode()))

        self.assertEqual(node_attrs - declared['Node'], set())
        self.assertEqual(
            kdnode_attrs - declared['Node'] - declared['KDNode'], set())


class TypingSampleTests(unittest.TestCase):
    """ The type-checked sample code also has to work at runtime """

    def test_sample_runs(self):
        typing_sample.main()


# Code that fails at runtime and therefore has to be rejected by the type
# checkers: {name: source}
INVALID_USAGE = {
    'k is an int': (
        'tree.search_knn((1, 2), "three")\n'
    ),
    'distance can not be negated': (
        'def dist(a: object, b: object, axis: int | None = None) -> str:\n'
        '    return "far"\n'
        'tree.search_knn((1, 2), 1, dist=dist)\n'
    ),
    'distance can not be None': (
        'tree.search_nn((1, 2), dist=lambda a, b, axis=None: None)\n'
    ),
    'dimensions of a set can not be inferred': (
        'kdtree.create({(1, 2), (3, 4)})\n'
    ),
    'dimensions of a set can not be checked': (
        'kdtree.check_dimensionality({(1, 2), (3, 4)})\n'
    ),
    'points can not be an iterator': (
        'kdtree.create(iter([(1, 2), (3, 4)]), dimensions=2)\n'
    ),
    'distance function without axis': (
        'def dist(a: object, b: object) -> int:\n'
        '    return 0\n'
        'tree.search_nn((1, 2), dist=dist)\n'
    ),
    'distance function for other point types': (
        'class Item:\n'
        '    coords = (0, 0)\n'
        '    def __len__(self) -> int:\n'
        '        return 2\n'
        '    def __getitem__(self, i: int) -> int:\n'
        '        return self.coords[i]\n'
        'def dist(a: Item, b: Item, *, axis: int | None) -> int:\n'
        '    return a.coords[0] - b.coords[0]\n'
        'tree.search_nn((1, 2), dist=dist)\n'
    ),
    'replacement of a single node is None': (
        'replacement, parent = tree.find_replacement()\n'
        'replacement.data\n'
    ),
}

INVALID_USAGE_HEADER = (
    'import kdtree\n'
    'tree = kdtree.create([(1, 2)])\n'
)


def write_invalid_usage(directory):
    """ Writes each INVALID_USAGE snippet to its own file """
    paths = {}
    for i, (name, source) in enumerate(sorted(INVALID_USAGE.items())):
        path = os.path.join(directory, 'invalid_%d.py' % i)
        with open(path, 'w') as f:
            f.write(INVALID_USAGE_HEADER + source)
        paths[name] = path
    return paths


class InvalidUsageTests(unittest.TestCase):
    """ The rejected snippets have to fail at runtime """

    def test_invalid_usage_fails_at_runtime(self):
        for name, source in INVALID_USAGE.items():
            with self.subTest(name):
                with self.assertRaises((TypeError, AttributeError, IndexError)):
                    exec(INVALID_USAGE_HEADER + source, {})


def run_checker(args):
    proc = subprocess.run(args, cwd=HERE, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, universal_newlines=True)
    return proc.returncode, proc.stdout


@unittest.skipUnless(has_module('mypy'), 'mypy is not installed')
class MypyTests(unittest.TestCase):

    def test_stub_is_valid(self):
        code, out = run_checker([sys.executable, '-m', 'mypy', '--strict',
                                 '--no-incremental', STUB])
        self.assertEqual(code, 0, out)

    def test_sample(self):
        code, out = run_checker([sys.executable, '-m', 'mypy', '--strict',
                                 '--no-incremental', SAMPLE])
        self.assertEqual(code, 0, out)

    def test_stubtest(self):
        """ mypy's stubtest compares the stub with the runtime module """
        code, out = run_checker([sys.executable, '-m', 'mypy.stubtest',
                                 'kdtree'])
        self.assertEqual(code, 0, out)

    def test_detects_errors(self):
        """ code that fails at runtime is rejected """
        with tempfile.TemporaryDirectory() as directory:
            for name, path in write_invalid_usage(directory).items():
                with self.subTest(name):
                    code, out = run_checker([
                        sys.executable, '-m', 'mypy', '--no-incremental',
                        '--cache-dir', os.devnull, path,
                    ])
                    self.assertNotEqual(code, 0, out)


@unittest.skipUnless(shutil.which('pyright'), 'pyright is not installed')
class PyrightTests(unittest.TestCase):

    def test_sample(self):
        code, out = run_checker(['pyright', '--pythonpath', sys.executable,
                                 SAMPLE, STUB])
        self.assertEqual(code, 0, out)

    def test_detects_errors(self):
        """ code that fails at runtime is rejected """
        with tempfile.TemporaryDirectory() as directory:
            for name, path in write_invalid_usage(directory).items():
                with self.subTest(name):
                    code, out = run_checker([
                        'pyright', '--pythonpath', sys.executable, path,
                    ])
                    self.assertNotEqual(code, 0, out)


@unittest.skipUnless(has_module('setuptools'), 'setuptools is not installed')
class PackagingTests(unittest.TestCase):
    """ The stub has to be installed along with the module """

    def test_build_installs_stubs(self):
        with tempfile.TemporaryDirectory() as build_lib:
            code, out = run_checker([
                sys.executable, os.path.join(HERE, 'setup.py'), '-q',
                'build_py', '--build-lib', build_lib,
            ])
            self.assertEqual(code, 0, out)

            with open(STUB) as f:
                stub = f.read()

            self.assertTrue(
                os.path.exists(os.path.join(build_lib, 'kdtree.py')))

            # next to the module, for type checkers that support this
            # (eg pyright)
            with open(os.path.join(build_lib, 'kdtree.pyi')) as f:
                self.assertEqual(f.read(), stub)

            # as a PEP 561 stub-only package, for mypy
            with open(os.path.join(build_lib, 'kdtree-stubs',
                                   '__init__.pyi')) as f:
                self.assertEqual(f.read(), stub)


if __name__ == '__main__':
    unittest.main()
