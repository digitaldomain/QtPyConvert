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

print("Finding packages: %s" % find_packages("src/python"))

setup(
    name="QtPyConvert",
    version=version,
    description="An automatic Python Qt binding transpiler to the Qt.py abstraction layer. It aims to help in your modernization of your Python Qt code. QtPyConvert supports the following bindings out of the box:\n    PyQt4\n    PySide\n    PyQt5\n    PySide2\nIt also has experimental support for defining your own bindings.",
    long_description=open("README.md").read(),
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
