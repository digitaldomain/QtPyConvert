
# QtPyConvert ![Digital Domain Logo](_resources/logo.gif "Digital Domain Logo")

* [Project Goals](#project-goals)
* [Getting Started](#getting-started)  
  * [Prerequisites](#prerequisites)
  * [Usage](#usage)
  * [Customization](#customization)
* [Converting](#converting)
* [Project Information](#project-information)
  * [Built With](#built-with)
  * [Contributing](#contributing)
  * [Versioning](#versioning)
  * [Authors](#authors)
  * [License](#license)
  * [Acknowledgments](#acknowledgments)
  



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

## Troubleshooting

QtPyConvert is still a bit of a work in progress, there are things that it cannot yet convert with 100% certainty.  
The following is a guide of common problems that you might have pop up.

### During Conversion

#### baron.parser.ParsingError

The most common thing that you will probably see is a Baron parsing error.  
```bash
Traceback (most recent call last):
  File "/usr/bin/qt_py_convert", line 47, in <module>
    main(args.file_or_directory, args.recursive, args.write)
  File "/usr/bin/qt_py_convert", line 40, in main
    process_folder(path, recursive=recursive, write=write)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 310, in process_folder
    process_folder(os.path.join(folder, fn), recursive, write, fast_exit)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 310, in process_folder
    process_folder(os.path.join(folder, fn), recursive, write, fast_exit)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 310, in process_folder
    process_folder(os.path.join(folder, fn), recursive, write, fast_exit)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 310, in process_folder
    process_folder(os.path.join(folder, fn), recursive, write, fast_exit)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 302, in process_folder
    os.path.join(folder, fn), write=write, fast_exit=fast_exit
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 282, in process_file
    aliases, mappings, modified_code = run(source, fast_exit=fast_exit)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/run.py", line 264, in run
    psep0101.process(red)
  File "/usr/lib/python2.7/site-packages/qt_py_convert/_modules/psep0101/process.py", line 215, in process
    getattr(Processes, issue)(red, psep_issues[issue]) if psep_issues[issue] else None
  File "/usr/lib/python2.7/site-packages/qt_py_convert/_modules/psep0101/process.py", line 34, in _process_qvariant
    node.parent.replace(changed)
  File "/usr/lib/python2.7/site-packages/redbaron/base_nodes.py", line 1016, in replace
    new_node = self._convert_input_to_node_object(new_node, parent=None, on_attribute=None, generic=True)
  File "/usr/lib/python2.7/site-packages/redbaron/base_nodes.py", line 156, in _convert_input_to_node_object
    return Node.from_fst(baron.parse(value)[0], parent=parent, on_attribute=on_attribute)
  File "/usr/lib/python2.7/site-packages/baron/baron.py", line 57, in parse
    to_return = _parse(tokens, print_function)
  File "/usr/lib/python2.7/site-packages/baron/baron.py", line 26, in _parse
    raise e
baron.parser.ParsingError: Error, got an unexpected token RIGHT_SQUARE_BRACKET here:
   1 self.user_data[index.row(]<---- here

The token RIGHT_SQUARE_BRACKET should be one of those: BACKQUOTE, BINARY, BINARY_RAW_STRING, BINARY_STRING, COMMA, COMPLEX, DOUBLE_STAR, FLOAT, FLOAT_EXPONANT, FLOAT_EXPONANT_COMPLEX, HEXA, INT, LAMBDA, LEFT_BRACKET, LEFT_PARENTHESIS, LEFT_SQUARE_BRACKET, LONG, MINUS, NAME, NOT, OCTA, PLUS, RAW_STRING, RIGHT_PARENTHESIS, STAR, STRING, TILDE, UNICODE_RAW_STRING, UNICODE_STRING

It is not normal that you see this error, it means that Baron has failed to parse valid Python code. It would be kind if you can extract the snippet of your code that makes Baron fail and open a bug here: https://github.com/Psycojoker/baron/issues

Sorry for the inconvenience.
```


Because we are using an alternate Python AST, there are sometimes issues on edge cases of code.
Unfortunately, Baron get's confused sometimes when it tries to send us a helpful traceback and the error is usually earlier than it thinks.    
There are two usual suspects when getting a Baron ParsingError.  


##### Incorrectly indented comments

This is a problem that will popup with Baron because it actually pays attention to the comments, whereas Python just throws them out.
If you are getting an error similar to the above, you will want to look higher in the script for incorrectly indented comments, multiline and single line ones.

##### Bare print statements

This is less common than the indented comments issue but has still shown up in a few cases for us internally.  
There are times where Baron cannot parse a print statement and turning it into a print function by enclosing it in parenthesis seems to fix it.


#### Qt.py does not support uic.loadUiType
The Qt.py module does not support uic.loadUiType.  
Please see [https://github.com/mottosso/Qt.py/issues/237](https://github.com/mottosso/Qt.py/issues/237)


### During Runtime

#### QLayout.setMargin
As of Qt 4.7 QLayout.setMargin has been set to obsolete which means that it will be removed.  
As it turns out, they removed it in Qt5.
The obsoleted page is [here](http://doc.qt.io/archives/qt-4.8/qlayout-obsolete.html)

Obsoleted code
> layout = QLayout()  
> layout.setMargin(10)

Replacement code  
> layout = QLayout()  
> layout.setContentsMargins(10, 10, 10, 10)  


## Future Features

There are several things that we would love to have support for in QtPyConvert but we just haven't gotten around to yet for various reasons.

- Warnings about deprecated/obsoleted method calls in Qt4 code.
  - There were many method calls that were removed in Qt5 and most people were unaware that they should be using something else when they wrote the Qt4 code.  
    There are lists on the Qt5 docs about what was deprecated and what the replacements are (if any) in Qt5 code. It would be nice if we could warn the user about these when we detect them and potentially automatically fix some of them too.
  - In a perfect world we would be able to dynamically build the list of these by scraping the Qt website too.
- Better support for api-v1.0 method removal. 
  Currently we are basially looking for the method names because they are quite unique. 
  Ideally it'd be great if we could somehow record the type of the object at least in locals and then if that object was a QString for example, see if it is using any methods that aren't on a builtin string type.
- Better support for the QtCompat.<Class>.method replacements. 
  Much of this would require the previous feature to be somewhat figured out. 
  We would need to at least minimally track variable types.



## Project Information

### Built With

* [Qt.py](https://github.com/mottosso/Qt.py) - The Qt abstraction library that we port code to.
* [RedBaron](https://github.com/PyCQA/Redbaron) - The alternate Python AST which allows us to modify and preserve comments + formatting.

### Contributing

Please read [CONTRIBUTING.md](https://github.com/DigitalDomain/QtPyConvert/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

### Versioning

We use [semantic versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/DigitalDomain/QtPyConvert/tags).

### Authors

* **Alex Hughes** - Initial work - [Digital Domain](https://digitaldomain.com)
* **Rafe Sacks**  - Prototyping help - [Digital Domain](https://digitaldomain.com)

See also the list of [contributors](https://github.com/DigitalDomain/QtPyConvert/contributors) who participated in this project.

### License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/DigitalDomain/QtPyConvert/LICENSE) file for details

### Acknowledgments

* [The developers of Qt.py](https://github.com/mottosso/Qt.py/contributors)
*  [The developers of RedBaron](https://github.com/PyCQA/redbaron/contributors)
* etc
