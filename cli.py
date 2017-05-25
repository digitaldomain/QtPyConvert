#!/tools/bin/python2.7

import re
from dd.runtime import api
api.load("qt_py")
from Qt import QtGui, QtWidgets, QtCore

def find_things(lines):
    capture_groups = []
    for index, line in enumerate(lines):
        match = re.search(r"(QtGui|QtCore)\.(\w+)", line)
        if match:
            mod, func = match.groups()
            if "capture_groups" not in locals():
                pass
            capture_groups.append((mod, func, index))
        match = re.search(r"from\s(PySide|PyQt4)\simport\s([\w\s,]+)", line)
        if match:
            mod, imports_ = match.groups()
            capture_groups.append((mod, imports_, index))
    return capture_groups

def test_things(things):
    bad = []
    for mod, func, line_index in things:
        if mod in ["PySide", "PyQt4"]:
            bad.append((mod, func, line_index))
            continue
        try:
            if mod == "QtGui":
                getattr(QtGui, func)
                bad.append((mod, func, line_index))
            elif mod == "QtCore":
                getattr(QtCore, func)
                bad.append((mod, func, line_index))
            else:
                print("What is %s" % mod.strip("\n"))
        except Exception:
            bad.append((mod, func, line_index))
    fixy = []
    for mod, func, line_index in bad:
        if mod in ["PySide", "PyQt4"]:
            correct_mod = "Qt"
            fixy.append((mod, correct_mod, func, line_index))
            continue
        try:
            getattr(QtGui, func)
            correct_mod = "QtGui"
        except:
            try:
                getattr(QtCore, func)
                correct_mod = "QtCore"
            except:
                try:
                    getattr(QtWidgets, func)
                    correct_mod = "QtWidgets"
                except:
                    correct_mod = mod
                    print("Could not fix (\"%s\", \"%s\")" % (mod.strip("\n"), func.strip("\n")))
        fixy.append((mod, correct_mod, func, line_index))
    return fixy


def fix(results, fp, text_lines):
    import_index = -1
    required_mods = []
    for orig, good, func, line_index in results:
        if good == "Qt":
            print("Found Qt imports. Line number is %s" % line_index)
            import_index = line_index
            continue
        if good not in required_mods:
            required_mods.append(good)
        print("Fixing line number %d: \"%s\"" % (line_index+1, text_lines[line_index].strip("\n")))
        text_lines[line_index] = text_lines[line_index].replace(orig, good)
    if import_index != -1:
        print("Fixing imports on line %d: \"%s\"" % (import_index+1, text_lines[import_index].strip("\n")))
        text_lines[import_index] = "from dd.runtime import api\napi.load(\"qt_py\")\nfrom Qt import {mods}\n".format(mods=", ".join(required_mods))
    with open(fp, "wb") as fh:
        fh.writelines(text_lines)


def do(path):
    with open(path, "rb") as fh:
        data = fh.readlines()
    results = test_things(find_things(data))
    for orig, good, func, line_index in results:
        if orig != good:
            print(
                "Changing to \"%s.%s\" from \"%s.%s\"."
                % (good.strip("\n"), func.strip("\n"), orig.strip("\n"), func.strip("\n"))
            )
    fix(results, path, data)

if __name__ == "__main__":
    import sys
    paths = sys.argv[-1]
    for path in paths.split(","):
        print("--" * 30)
        print("Running on \"%s\"" % path.strip())
        print("--" * 30)
        do(path.strip())
        print("--" * 30)
        print("--" * 30)
        print("")

# TODO: Better imports when I replace. Currently is it <old> + <new>
# TODO: Make this poor POS code better, docstrings, function names, general sensibility, etc
