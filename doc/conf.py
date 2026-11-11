# Sphinx configuration for the python-kdtree documentation
#
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# kdtree is a single module in the parent directory
sys.path.insert(0, os.path.abspath('..'))

import kdtree

project = 'python-kdtree'
author = 'Stefan Kögl'
copyright = kdtree.__author__
version = release = kdtree.__version__

# the first line of the module docstring
description = kdtree.__doc__.strip().splitlines()[0]

extensions = ['sphinx.ext.autodoc']

root_doc = 'index'
exclude_patterns = ['_build']

# document members in the order of the source file, not alphabetically
autodoc_member_order = 'bysource'

html_theme = 'classic'

latex_documents = [
    ('index', 'python-kdtree.tex', 'python-kdtree Documentation', author,
     'manual'),
]

man_pages = [
    ('index', 'python-kdtree', 'python-kdtree Documentation', [author], 1),
]

texinfo_documents = [
    ('index', 'python-kdtree', 'python-kdtree Documentation', author,
     'python-kdtree', description, 'Miscellaneous'),
]
