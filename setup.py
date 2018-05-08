import os
from setuptools import setup, find_packages
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))
version = __import__("qt_py_convert").__version__


classifiers = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.5",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Utilities"
]

long_description = """
QtPyConvert
===========

-  `Project Goals <#project-goals>`__
-  `Project Information <#project-information>`__
-  `Built With <#built-with>`__
-  `Contributing <#contributing>`__
-  `Authors <#authors>`__
-  `License <#license>`__

An automatic Python Qt binding transpiler to the `Qt.py abstraction
layer <https://github.com/mottosso/Qt.py>`__. It aims to help in your
modernization of your Python Qt code. QtPyConvert supports the following
bindings out of the box: \*
`PyQt4 <https://www.riverbankcomputing.com/software/pyqt/download>`__ \*
`PySide <http://pyside.github.io/docs/pyside/>`__ \*
`PyQt5 <https://www.riverbankcomputing.com/software/pyqt/download5>`__
\* `PySide2 <https://wiki.qt.io/PySide2>`__

It also has experimental support for defining your own bindings. > See
`customization <#customization>`__ for more information

Project Goals
-------------

Convert any code using any of the four major Qt for Python bindings into
the standardized `Qt.py abstraction
layer <https://github.com/mottosso/Qt.py>`__.

Warn users about incompatibilities or unsupported code. (WIP)

Standardize Qt imports to maintain sanity in code comprehension. >
Removing start imports and deep class/module imports

Project Information
-------------------

Built With
~~~~~~~~~~

-  `Qt.py <https://github.com/mottosso/Qt.py>`__ - The Qt abstraction
   library that we port code to.
-  `RedBaron <https://github.com/PyCQA/Redbaron>`__ - The alternate
   Python AST which allows us to modify and preserve comments +
   formatting.

Contributing
~~~~~~~~~~~~

Please read
`CONTRIBUTING.md <https://github.com/DigitalDomain/QtPyConvert/blob/master/CONTRIBUTING.md>`__
for details on our code of conduct, and the process for submitting pull
requests to us.

Authors
~~~~~~~

-  **Alex Hughes** - Initial work - `Digital
   Domain <https://digitaldomain.com>`__
-  **Rafe Sacks** - Prototyping help - `Digital
   Domain <https://digitaldomain.com>`__

See also the list of
`contributors <https://github.com/DigitalDomain/QtPyConvert/contributors>`__
who participated in this project.

License
~~~~~~~

This project is licensed under a modified Apache 2.0 license - see the
`LICENSE <https://github.com/DigitalDomain/QtPyConvert/blob/master/LICENSE>`__
file for details
"""

print("Finding packages: %s" % find_packages("src/python"))

setup(
    name="QtPyConvertTEST8",
    version=version,
    description="An automatic Python Qt binding transpiler to the Qt.py abstraction layer. It aims to help in your modernization of your Python Qt code. QtPyConvert supports the following bindings out of the box: PyQt4, PySide, PyQt5, PySide2. It also has experimental support for defining your own bindings.",
    long_description=long_description,
    author="Alex Hughes",
    author_email="ahughesalex@gmail.com",
    url="https://github.com/digitaldomain/QtPyConvert",
    license="Modified Apache 2.0",
    zip_safe=False,
    data_files=["LICENSE"],
    install_requires=open("requirements.txt").readlines(),
    package_dir={"":"src/python"},
    packages=find_packages("src/python"),
    classifiers=classifiers
)
