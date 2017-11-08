#
# Confidential and Proprietary Source Code
#
# This Digital Domain Productions, Inc. source code, including without
# limitation any human-readable computer programming code and associated
# documentation (together "Source Code"), contains valuable confidential,
# proprietary and trade secret information of Digital Domain Productions and is
# protected by the laws of the United States and other countries. Digital
# Domain Productions, Inc. may, from time to time, authorize specific employees
# to use the Source Code internally at Digital Domain Production Inc.'s premises
# solely for developing, updating, and/or troubleshooting the Source Code. Any
# other use of the Source Code, including without limitation any disclosure,
# copying or reproduction, without the prior written authorization of Digital
# Domain Productions, Inc. is strictly prohibited.
#
# Copyright (c) [2011] Digital Domain Productions, Inc. All rights reserved.
#
"""
DD documentation build configuration file. Originally created by
sphinx-quickstart on Mon Oct 31 09:57:48 2011.

Package configuration code added on 2014-06-14

This file is execfile()d with the current directory set to its containing dir.

Note that not all possible configuration values are present in this file.
"""
import os
import sys
import getpass
import datetime

try:
    from os.path import relpath as _relpath
except ImportError:  # Backwards compatible for python 2.5
    print (
        "os.path.relpath raise an ImportError. "
        "Using backwards compatability function..."
    )

    def _relpath(path, start=os.curdir):
        """Return a relative version of a path"""
        from os.path import curdir, sep, pardir, join, abspath, commonprefix

        if not path:
            raise ValueError("No path specified")

        start_list = abspath(start).split(sep)
        path_list = abspath(path).split(sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir

        return join(*rel_list)
    # end _relpath
# end try

import dd.runtime.api

#
# force use of our local package for sphinx grokking, otherwise we get whatever package the
# current environment resolves, which is completely de-synced from ddautoapi on local package.
#
path = os.path.join(os.path.abspath('..'), 'private', 'build', 'qt_py_convert', 'python')
sys.path.insert(0, path)
import qt_py_convert

# Load the facility's extensions and themes. This offer to the user a
# bunch of themes and extensions maintained for the studio.
dd.runtime.api.load("sphinx_extensions")
import sphinx_extensions

SPHINX_EXTENSIONS_THEMES_PATH = os.path.abspath(sphinx_extensions.getThemesPath())
#dirname = os.path.abspath(os.path.dirname(__file__))
#SPHINX_EXTENSIONS_THEMES_PATH = _relpath(sphinx_extensions.getThemesPath(), dirname)

#
# Constants...  ----------------------------------------------------------------
#
PACKAGE_NAME = os.environ["PACKAGE_NAME"]
PACKAGE_VERSION = os.environ["PACKAGE_VERSION"]
PACKAGE_ROOT = os.environ["PACKAGE_ROOT"]

AUTHOR = getpass.getuser()

try:
    PACKAGE_VERSION_MAJOR, PACKAGE_VERSION_MINOR = PACKAGE_VERSION.split(".", 2)
except ValueError:
    PACKAGE_VERSION_MAJOR = PACKAGE_VERSION_MINOR = ""

BUILD_ROOT = os.path.join(PACKAGE_ROOT, "private", "build", PACKAGE_NAME)
BUILD_PYTHON_ROOT = os.path.join(BUILD_ROOT, "python")

#MAYA_SCRIPTS_ROOT = os.path.join(BUILD_ROOT, "maya", "scripts", PACKAGE_NAME)

CONF_ABS_DIR = os.path.abspath(os.path.dirname(__file__))
EXTENSIONS_PATH = os.path.join(CONF_ABS_DIR, "_ext")

print "using python: %s" % sys.executable

print "conf.py using..."
print " - PACKAGE_NAME:      %s" % PACKAGE_NAME
print " - PACKAGE_VERSION:   %s" % PACKAGE_VERSION
print " - AUTHOR:            %s" % AUTHOR
print " - PACKAGE_ROOT:      %s" % PACKAGE_ROOT
print " - BUILD_ROOT:        %s" % BUILD_ROOT
assert os.path.exists(PACKAGE_ROOT)
print " - BUILD_PYTHON_ROOT: %s" % BUILD_PYTHON_ROOT
assert os.path.exists(BUILD_ROOT)
print " - CONF_ABS_DIR:      %s" % CONF_ABS_DIR
assert os.path.exists(BUILD_PYTHON_ROOT)
print " - EXTENSIONS_PATH:   %s" % EXTENSIONS_PATH
assert os.path.exists(CONF_ABS_DIR)
#print " - MAYA_SCRIPTS_ROOT: %s" % MAYA_SCRIPTS_ROOT
#assert os.path.exists(MAYA_SCRIPTS_ROOT)
print " - SPHINX_EXTENSIONS_THEMES_PATH:   %s" % SPHINX_EXTENSIONS_THEMES_PATH
assert os.path.exists(SPHINX_EXTENSIONS_THEMES_PATH)


#EXTENSIONS_PATH
# Environment Setup...  --------------------------------------------------------
#
# Extensions specific to this package should be placed under the "_ext"
# directory, next to this file.  We place the path in "sys.path"
# even if the folder does not exist.
sys.path.insert(0, EXTENSIONS_PATH)

# If this package contains python code, we will add the python root
# to "sys.path" for modules to be automatically discoverable by sphinx.
sys.path.insert(0, BUILD_PYTHON_ROOT)

# Maya scripts have to be directly on the Python path to work. Add each folder
# sys.path.insert(0, os.path.join(MAYA_SCRIPTS_ROOT, "steps"))
# sys.path.insert(0, os.path.join(MAYA_SCRIPTS_ROOT, "steps", "tests"))

# This variable is required for the `preferences` package to
# properly find the preference files.
os.environ["%s_PACKAGE_ROOT" % PACKAGE_NAME.upper()] = BUILD_ROOT

# We need these modules to be importable to mock the maya API.
# XXX: should they be distributed with the package if they are just mocks?
# fake_mods_dir = os.path.join(PACKAGE_ROOT, "resources", "sphinx_fake_modules")
# print " - Adding fake modules (mocks): %s" % fake_mods_dir
# assert os.path.exists(fake_mods_dir)
# sys.path.insert(0, fake_mods_dir)

#
# General configuration...
#
# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = "1.0"

# General information about the project.
project = u"%s" % PACKAGE_NAME
year = datetime.datetime.now().year
copyright = u"%s, Digital Domain Productions, Inc. All rights reserved" % year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "%s.%s" % (PACKAGE_VERSION_MAJOR, PACKAGE_VERSION_MINOR)
# The full version, including alpha/beta/rc tags.
release = PACKAGE_VERSION

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ""

# Else, today_fmt is used as the format for a strftime call.
#today_fmt = "%B %d, %Y"

# The encoding of source files.
#source_encoding = "utf-8-sig"

# The suffix of source filenames.
source_suffix = ".rst"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, "()" will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# By default, highlight as Python.
highlight_language = "python"

# The name of the Pygments (syntax highlighting) style to use.
# Overriding whatever is set in the theme's theme.conf.
#pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    # "sphinx.ext.intersphinx",          # cross-reference other package"s docs
    "sphinx.ext.autodoc",              # automatic API documentation
    "sphinx.ext.autosummary",          # automatic API documentation
    "sphinx.ext.viewcode",             # including links to source code
    "sphinx.ext.todo",                 # highlighting
    # "sphinx.ext.inheritance_diagram",  # inheritance-diagram directive
    # "sphinxcontrib.httpdomain",        # document REST APIs
    "sphinx_extensions.betterdocs",    # extend the builtin extensions
    # "sphinx_extensions.jsonhilight",   # add support for json highlighting
    # "sphinx_extensions.meldomain",     # add support for mel highlighting
    "sphinx_extensions.require",       # add support for package loading
    'sphinx_extensions.ddautoapi',     # better automatic api documentation (0.4.3 req)
]

#
# Builtin-extensions configuration...  -----------------------------------------
#
## sphinx.ext.autosummary --------------------------------------------------

# Boolean indicating whether to scan all found documents for autosummary
# directives, and to generate stub pages for each.
# Can also be a list of documents for which stub pages should be generated.
# The new files will be placed in the directories specified in the
# :toctree: options of the directives.
#autosummary_generate = True

## sphinx.ext.autodoc ------------------------------------------------------

# You can choose which docstring will be picked to document a class's main body:
# - "class": use the class' docstring (default)
# - "init": use the __init__ methods docstring
# - "both": the class' and the __init__ method's docstring are concatenated
autoclass_content = "both"

# Select the sort order for documented members:
# - "alphabetical": the default.
# - "groupwise": by member type (function, classmethod, attributes...)
# - "bysource": the order they are defined.
autodoc_member_order = "bysource"

# The list of autodoc directive flags that should be automatically applied.
# The supported flags are "members", "undoc-members", "private-members",
# "special-members", "inherited-members" and "show-inheritance".
autodoc_default_flags = [
    "members",
    "undoc-members",
    "show-inheritance",
    "private-members",
]

# autodoc_mock_imports doesn't seem to work (below)
import mock
for mod in ["qt_py_convert.external"]:
    sys.modules[mod] = mock.MagicMock()

# The list of modules to be mocked up (some external dependencies may
# not be met at build time and break the building process).
# autodoc_mock_imports = [
#     "maya",
#     "maya.cmds",
#     "nuke",
#     "hou",
# ]
## sphinx.ext.intersphinx --------------------------------------------------

# print "Loading packages..."
#
# print "  - dd.runtime.api.load('qt_py_convert')..."
# dd.runtime.api.load('qt_py_convert')
# import qt_py_convert


#
# Contains the locations and names of other projects that should be
# linked to in this documentation.
#
# FIXME: doesn't work now that internet access cut off:
intersphinx_mapping = {}#"python": ("http://docs.python.org/2.7", None)}

## sphinx.ext.inheritance_diagram ------------------------------------------

# A dictionary of graphviz graph attributes for inheritance diagrams.
inheritance_graph_attrs = {
    "rankdir": "TB",
    "size": '"6.0, 6.0"',
    "fontsize": 14,
    "ratio": "compress",
}

# A dictionary of graphviz node attributes for inheritance diagrams.
#inheritance_node_attrs = {}

# A dictionary of graphviz edge attributes for inheritance diagrams.
#inheritance_edge_attrs = {}

## sphinx.ext.autosummary --------------------------------------------------

autosummary_generate = True

## ddautoapi: auto api rst generation --------------------------------------

ddautoapi_python_dirs = [
    os.path.join(BUILD_ROOT, "python")
]

ddautoapi_module_roots = [
    PACKAGE_NAME,
]

ddautoapi_exclude_modules = [
    "qt_py_convert.external",
]

#
# DigitalDomain-extensions configuration...  -----------------------------------
#
## sphinx_extensions.require -----------------------------------------------

# Provide your own space-separated list of other packages that you want to
# be loaded when documentation is generated. Note - a specific version
# of a package may be specified such as in "alembic==1.2.3". The
# "sphinx_extensions.require" must be listed as extensions.

## sphinx_extensions.betterdocs --------------------------------------------

# Instances of this class are used by the HTML builder.  Put the full python
# path to the class.
#html_translator_class = "sphinx_extensions.betterdocs.CustomHtmlTranslator"


#
# Options for HTML output...  --------------------------------------------------
#
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = "xhaiku"
html_theme = "xtravagantdd"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {"collapsiblesidebar": True}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [SPHINX_EXTENSIONS_THEMES_PATH]

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "%s %s Documentation" % (PACKAGE_NAME, release)

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar
# html_logo = "images/header-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If not "", a "Last updated on:" timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ""

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
#htmlhelp_basename = PACKAGE_NAME


#
# Options for LaTeX output...  -------------------------------------------------
#
# The paper size ("letter" or "a4").
#latex_paper_size = "letter"

# The font size ("10pt", "11pt" or "12pt").
#latex_font_size = "10pt"

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual])
latex_documents = [
    (
        "index",
        "%s.tex" % PACKAGE_NAME,
        u"%s Documentation" % PACKAGE_NAME,
        AUTHOR,
        "manual"
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = "images/header-logo.png"

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ""

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


#
# Options for manual page output...  -------------------------------------------
#
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "index",
        PACKAGE_NAME,
        u"%s Documentation" % PACKAGE_NAME,
        [AUTHOR],
        1
    )
]

print "Done loading %s" % __file__
