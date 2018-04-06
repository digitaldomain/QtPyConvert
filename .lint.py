#!/usr/bin/env python2.7
"""pylint runner"""

# python
import os
import sys
import StringIO

# pylint
from pylint import lint as linter
from pylint.reporters.text import TextReporter


package_name = 'qt_py_convert'

# wrappers, other dirs
cwd = os.getcwd()
extra_dirnames = [
    os.path.join(cwd, 'src', 'bin'),
]

# force use of 1.5.6-style pylint rc for now:
lint_flavor = 'critical'
lint_rc = '.pylint.rc'


def lint(path, output, extra_pythonpath=None):

    args = [
        '-r', 'n',
        '--rcfile=' + lint_rc,
    ]

    buf = StringIO.StringIO()
    linter.Run([path] + args, reporter=TextReporter(buf), exit=False)

    stdout = buf.getvalue()
    if output:
        output.write(stdout)
    sys.stdout.write(stdout)

    return len(stdout) == 0


def lint_directory(dcc_scripts, output, extra_pythonpath=None, fingerprint_all=False):

    clean_code = True

    elides = []
    for dirname, _subdirs, filenames in os.walk(dcc_scripts):

        basename = os.path.basename(dirname)

        # hack for layoutpipeline tests, don't go into SHOW directories
        if 'tests' in dirname:
            all_caps = True
            for char in basename:
                if not char.isdigit() and not char.isupper():
                    all_caps = False
                    break

            if all_caps:
                #print >> sys.stderr, 'skip presumed SHOW directory "%s"' % basename
                elides.append(dirname)
                continue

            if basename in ('local', 'utilities'):
                elides.append(dirname)
                continue
        if "external" == dirname:
            elides.append(dirname)
            continue

        # don't recurse into elided dirs.  think there is a filter arg on walk,
        is_elided = False
        for elide in elides:
            if dirname.startswith(elide):
                is_elided = True
                break
        if is_elided:
            continue

        # skip things like .svn
        if not basename[0].isalpha():
            elides.append(dirname)
            continue

        # if we have a package, stop here
        if os.path.exists(os.path.join(dirname, '__init__.py')):
            clean_code &= lint(dirname, output, extra_pythonpath)

            # assume now if we were under a package, we don't wish to recurse again.
            elides.append(dirname)

        else:
            # run lint on all python files within dir.
            for filename in filenames:
                if filename.endswith('~'):
                    continue

                # hack: blacklist auto-generated qt ui files
                if filename.startswith('Ui_'):
                    continue

                if os.path.splitext(filename)[1] == '.py':
                    clean_code &= lint(os.path.join(dirname, filename), output, extra_pythonpath)
                elif fingerprint_all:
                    is_python = False
                    path = os.path.join(dirname, filename)
                    with open(path) as f:
                        first_line = f.readline()
                        # look for shebangs / dd boilerplate
                        if first_line.startswith('#') and \
                           ('python' in first_line or \
                           'No shebang line. This file is meant to be imported.' in first_line):
                            is_python = True
                    if is_python:
                        clean_code &= lint(path, output, extra_pythonpath)

    return clean_code


pylint_filename = 'pylint' + (('.' + lint_flavor) if lint_flavor else '') + '.out'

# eventual status
clean_code = True

if len(sys.argv) > 1:
    paths = sys.argv[1:]
    for path in paths:
        clean_code &= lint(path, None)

    sys.exit(0 if clean_code else 1)

# package
package_dirname = os.path.join(cwd, 'src', 'python', package_name)
lint_path = os.path.join(package_dirname, pylint_filename)
with open(lint_path, 'w') as output:
    clean_code &= lint(package_dirname, output)


for extra_dirname in extra_dirnames:
    lint_path = os.path.join(extra_dirname, pylint_filename)
    with open(lint_path, 'w') as output:
        clean_code &= lint_directory(extra_dirname, output, fingerprint_all=True)

# indicate success only in critical mode
if lint_flavor == 'critical':
    if not clean_code:
        print '# lint critical: your code is not clean'
        sys.exit(1)
    else:
        print '# lint critical: your code is clean, congrats!'
