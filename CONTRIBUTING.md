## Contributing to QtPyConvert

Thanks for taking the time to contribute!

In here you'll find a series of guidelines for how you can make QtPyConvert better suit your needs and the needs of the target audience - film, games and tv.

QtPyConvert was born to help companies with large legacy codebases convert their code in a timely manner and also to help the industry standardize on [Qt.py](https://github.com.mottosso/Qt.py).

**Table of contents**

- [Development goals](#development-goals)
  - [Converting Binding Support](#converting-binding-support)
  - [Incompatibility Warnings](#incompatibility-warnings)
  - [Keep it simple](#keep-it-simple)
  - [Normalize Imports](#normalize-imports)
- [How can I contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Style](#style)
  - [Commits](#commits)
  - [Version bumping](#version-bumping)
  - [Making a release](#making-a-release)

<br>

### Development Goals

QtPyConvert aims to help in the conversion of old Qt for Python code by automating the large majority of the work for you. It does this efficiently by leaving much of the work up to the Qt.py developers and using the resulting abstraction layer as a guideline and framework. 


Convert any code using any of the four major Qt for Python bindings into the standardized [Qt.py abstraction layer](https://github.com/mottosso/Qt.py).  
  
Warn users about incompatibilities or unsupported code. (WIP)

Standardize Qt imports to maintain sanity in code comprehension.   
> <sub>Removing start imports and deep class/module imports</sub>  


| Goal                       | Description
|:---------------------------|:---------------
| [*Convert code from any of the four major bindings.*](#converting-binding-support) | We should support everything that Qt.py does.
| [*Warn about incompatibilities.*](#incompatibility-warnings)       | If code cannot be converted or functionality is unsupported in Qt.py, we should warn.
| [*Keep it simple*](#keep-it-simple)       | Limit the heavy lifting, PEP008.
| [*Normalize import format*](#normalize-imports)          | Imports should be *sane* and normalized..

Each of these deserve some explanation and rationale.

<br>

##### Converting Binding Support

Running QtPyConvert should work on any source file, even if it doesn't use any Qt code. It should also have first party support for any bindings that Qt.py supports. Additional support for custom bindings either developed inhouse or online <sub>see pycode.qt</sub>, should have a way to be defined either through environment variables or a supplimentary site package that we look for.

<br>

##### Incompatibility Warnings

Several patterns are unsupported using Qt.py, these include but are not limited to **QVariants**, **QStrings**, and other Api-1.0 code. These should either be automatically converted, or at the  very least, printed out as a warning that the user can look into themselves.  
Ideally, it would be good to let users know about deprecated Qt code and provide a flag to attempt converting this as well.

##### Keep it simple

QtPyConvert is mainly a conversion wrapper around Qt.py.  
It tries to read what Qt.py is doing by looking at it's private values.  

Ideally we don't want QtPyConvert doing much conversion logic related to the actual mapping of methods and classes.    
Instead, we want to pay attention to api1.0 to api2.0 problems, Qt4  to Qt5 deprecation problems and to a certain extent, the Qt.py QtCompat changes.

<br>

##### Normalize Imports

One of the design decisions that was made early on was to normalize all Qt imports.  
This was partially due to preference and partially to step around the complications that would arise from keeping all of the deep level imports.

```python
# *Wrong*
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QCheckBox as chk
from PyQt4.QtCore.Qt import Unchecked, Checked

def click(state):
   print("Foo!")

c = chk()
c.clicked.stateChanged(click, Qt.QueuedConnection)
c.setCheckState(UnChecked)
```
```python
# *Right*
from Qt import QtCore, QtWidgets

def click(state):
   print("Foo!")

c = QtWidgets.QCheckBox()
c.clicked.stateChanged(click, QtCore.Qt.QueuedConnection)
c.setCheckState(QtCore.Qt.UnChecked)
```

This is one of the most notable *opinions* that QtPyConvert will enforce upon your code.
Another notable one that it will enforce is shown below
```python
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore.Qt import *

app = QApplication([])
app.setLayoutDirection(RightToLeft)
widget = QWidget()
widget.show()
app.exec_()
```

```python
from Qt import QtWidgets, QtCore

app = QtWidgets.QApplication([])
app.setLayoutDirection(QtCore.Qt.RightToLeft)
widget = QtWidgets.QWidget()
widget.show()
app.exec_()
```

It is bad practice to use star imports and unless you tell it not to, QtPyConvert will resolve your imports and pare them down.

<br>

## How can I contribute?

Contribution comes in many flavors, some of which is simply notifying us of problems or successes, so we know what to change and not to change.

### Contributor License Agreement

Before contributing code to QtPyConvert, we ask that you sign a Contributor License Agreement (CLA).  At the root of the repo you can find the two possible CLAs:

 - QtPyConvert_CLA_Corporate.md: please sign this one for corporate use
 - QtPyConvert_CLA_Individual.md: please sign this one if you're an individual contributor

Once your CLA is signed, send it to opensource@d2.com (please make sure to include your github username) and wait for confirmation that we've received it.  After that, you can submit pull requests.


### Reporting bugs

Bug reports must include:

1. Description
2. Expected results
3. Short reproducible

### Suggesting enhancements

Feature requests must include:

1. Goal (what the feature aims to solve)
2. Motivation (why *you* think this is necessary)
3. Suggested implementation (pseudocode)

Questions may also be submitted as issues.

### Pull requests

Code contributions are made by (1) forking this project and (2) making a modification to it. Ideally we would prefer it preceded by an issue where we discuss the feature or problem on a conceptual level before attempting an implementation of it.

This is where we perform code review - where we take a moment to look through and discuss potential design decisions made towards the goal you aim.

Your code will be reviewed and merged once it:

1. Does something useful
1. Provides a use case and example
1. Includes tests to exercise the change
1. Is up to par with surrounding code

The parent project ever only contains a single branch, a branch containing the latest working version of the project.

We understand and recognise that "forking" and "pull-requests" can be a daunting aspect for a beginner, so don't hesitate to ask. A pull-request should normally follow an issue where you elaborate on your desires; this is also a good place to ask about these things.

<br>

## Style

Here's how we expect your code to look and feel like.

### Commits

Commits should be well contained, as small as possible (but no smaller) and its messages should be in present-tense, imperative-style.

E.g.

```bash
# No
Changed this and did that

# No
Changes this and does that

# Yes
Change this and do that
```

The reason is that, each commit is like an action. An event. And it is perfectly possible to "cherry-pick" a commit onto any given branch. In this style, it makes more sense what exactly the commit will do to your code.

- Cherry pick "Add this and remove that"
- Cherry pick "Remove X and replace with Y"

### Version bumping

This project uses [semantic versioning](http://semver.org/) and is updated *after* a new release has been made.

For example, if the project had 100 commits at the time of the latest release and has 103 commits now, then it's time to increment. If however you modify the project and it has not yet been released, then your changes are included in the overall next release.

The goal is to make a new release per increment.

### Making a Release

Once the project has gained features, had bugs sorted out and is in a relatively stable state, it's time to make a new release.

- [https://github.com/DigitalDomain/QtPyConvert/releases](https://github.com/DigitalDomain/QtPyConvert/releases)

Each release should come with:

- An short summary of what has changed.
- A full changelog, including links to resolved issues.
 




<br>
<br>
Good luck and see you soon!


<br>
<br>
<br>