# QtPyConvert

An automatic Python Qt binding transpiler to the [Qt.py abstraction layer](https://github.com/mottosso/Qt.py). It aims to help in your modernization of your Python Qt code. QtPyConvert supports the following bindings out of the box:
  * [PyQt4](https://www.riverbankcomputing.com/software/pyqt/download)
  * [PySide](http://pyside.github.io/docs/pyside/)
  * [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)
  * [PySide2](https://wiki.qt.io/PySide2)

It also has experimental support for defining your own bindings.
> <sub>See [customization](#customization) for more information</sub>


## Project Goals
Convert any code using any of the four major Qt for Python bindings into the standardized [Qt.py abstraction layer](https://github.com/mottosso/Qt.py).

Warn users about incompatibilities or unsupported code. (WIP)

Standardize Qt imports to maintain sanity in code comprehension.
> <sub>Removing start imports and deep class/module imports</sub>

## Getting Started

When using **QtPyConvert**, developers should be aware of any [shortcomings](https://github.com/mottosso/Qt.py/blob/master/CAVEATS.md) of Qt.py or its [subset](https://github.com/mottosso/Qt.py#subset-or-common-members) of [supported features](https://github.com/mottosso/Qt.py#class-specific-compatibility-objects).

Basically read the README in the Qt.py project and be aware of what it does and does not do.

### Prerequisites

**QtPyConvert** reads the private values of the [Qt.py project](https://github.com/mottosso/Qt.py) to build it's internal conversion processes. To install this run
```
pip install Qt.py
```
**QtPyConvert** also uses [RedBaron](https://github.com/PyCQA/Redbaron) as an alternate abstract syntax tree.
Redbaron allows us to modify the source code and write it back out again, preserving all comments and formatting.
```
pip install redbaron
```

You should also have access to any of your source bindings so that Qy.py can import them freely.


### Usage
```bash
$ qt_py_convert [-h] [-r --recursive] [-w|-o] [--show-lines] [--to-method-support]
                files_or_directories [files_or_directories ...]
```

| Argument				| Description |
| --------------------- | ------------- |
| -h,--help				| Show the help message and exit. |
| files_or_directories	| Pass explicit files or directories to run. <sub>**NOTE:**</sub> If **"-"** is passed instead of files_or_directories, QtPyConvert will attempt to read from stdin instead. <sub>**Useful for pipelining proesses together**</sub> |
| -r,--recursive		| Recursively search for python files to convert. Only applicable when passing a directory.  |
| -w, --write			| Optionally pass a root directory to mirror the newly converted source code to.  |
| -o, --overwrite 		| Overwrite the files in place. **Either "-o" or "-w" must be passed to QtPyConvert if you want files to be written to disk.** |
| --show-lines			| Turn on printing of line numbers while replacing statements. Ends up being much slower. |
| --to-method--support 	| <sub>**EXPERIMENTAL**</sub>: An attempt to replace all api1.0 style "*toString*", "*toInt*", "*toBool*", "*toPyObject*", "*toAscii*" methods that are unavailable in api2.0. |

*If you don't pass "-o" or "-w <path>" to QtPyConvert, it will write to stdout.*


### Customization

QtPyConvert supports some custom bindings if you are willing to do a little bit of work.  

This is done through environment variables:
| Key                           | Value                                                                          | Description |
| ----------------------------- | ------------------------------------------------------------------------------ | ----------- |
| QT_CUSTOM_BINDINGS_SUPPORT    | The names of custom abstraction layers or bindings separated by **os.pathsep** | This can be used if you have code that was already doing it's own abstraction and you want to move to the Qt.py layer. |
| CUSTOM_MISPLACED_MEMBERS      | This is a json dictionary that you have saved into your environment variables. | This json dictionary should look similar to the Qt.py _misplaced_members dictionary but instead of mapping to Qt.py it maps the source bindings to your abstraction layer. |

> **Note** This feature is *experimental* and has only been used internally a few times. Support for this feature will probably be slower than support for the core functionality of QyPyConvert.


## Built With

* [Qt.py](https://github.com/mottosso/Qt.py) - The Qt abstraction library that we port code to.
* [RedBaron](https://github.com/PyCQA/Redbaron) - The alternate Python AST which allows us to modify and preserve comments + formatting.

## Contributing

Please read [CONTRIBUTING.md](https://github.com/DigitalDomain/QtPyConvert/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [semantic versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/DigitalDomain/QtPyConvert/tags).

## Authors

* **Alex Hughes** - Initial work - [Digital Domain](https://digitaldomain.com)
* **Rafe Sacks**  - Prototyping help - [Digital Domain](https://digitaldomain.com)

See also the list of [contributors](https://github.com/DigitalDomain/QtPyConvert/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/DigitalDomain/QtPyConvert/LICENSE) file for details

## Acknowledgments

* [The developers of Qt.py](https://github.com/mottosso/Qt.py/contributors)
*  [The developers of RedBaron](https://github.com/PyCQA/redbaron/contributors)
* etc
