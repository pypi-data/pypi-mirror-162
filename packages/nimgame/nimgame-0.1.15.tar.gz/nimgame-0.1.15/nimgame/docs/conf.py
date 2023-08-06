# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# Insert the package path first, so that the package __init__ is found first
# before the source/__init__ module
import sys, pathlib
sys.path.insert(0, str(pathlib.Path('..').resolve()))
sys.path.insert(1, str(pathlib.Path('../source').resolve()))

# -- Project information -----------------------------------------------------

project = 'nimgame'
copyright = '2022, netcreator'
author = 'netcreator'

# The full version, major, minor, patch (taken from the source/version.py)
import version as ver
release = ver.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon', 
    'sphinx.ext.autodoc', 
    'sphinx.ext.autosummary', 
    'sphinx.ext.viewcode', 
    'sphinx.ext.intersphinx', 
]

# Config of extensions
napoleon_preprocess_types = True
autosummary_generate = False
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.7', None)
}

# Packages not to be imported and considered by Sphinx
autodoc_mock_imports = ["js"]

# Make clases and types available as aliases
autodoc_type_aliases = dict( 
    Nim='Nim', 
    Move='Move', 
    ErrorRate_T='typedefs.ErrorRate_T', 
    HeapCoinRange_T='typedefs.HeapCoinRange_T', 
    MyTurn_T='typedefs.MyTurn_T', 
)
autodoc_typehints_format = 'short'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Source Code display width correction
html_css_files = [
    'srccode_width_correction.css',
]
