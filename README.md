The ``qt_py_convert`` package
=============================


**Welcome to ``qt_py_convert``**

*A utility for converting python qt binding code to Qt.py.*

<!--  NO DOCS YET
[v0.1.0 documentation](http://intranet.d2.com/dd/tools/cent6_64/package/ddg/0.1.0/docs/html/index.html)
-->

This project maintains a [CHANGELOG](CHANGELOG.md).

Developers should read [CONTRIBUTING](CONTRIBUTING.md) to get started.


Some Simple Goals
-----------------
1. Use simple python flow control over complex regular expressions unless readability or performance suffers (usually it is the opposite). This should create easier to maintainable code. 
2. Use generators with a clear single responsibility where ever possible. These are like plugins which handle a specific conversion and but can still have state survive to the next line. This will aid in collaboration and make test-driven development easier.
3. Use a global dry-run state to, when True, skip editing and display printed reports instead.
4. Support all four major bindings as well as attempt to allow "custom" binding support. For example ddg.gui
5. Develop a robust parsing engine, attempting to use simple python where applicable. Using more complex methods, like ast parsing when needed.