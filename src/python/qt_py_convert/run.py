import os
from pprint import pprint
import re
import traceback


from qt_py_convert.external import Qt
from qt_py_convert.external import redbaron

from qt_py_convert._modules import from_imports
from qt_py_convert._modules import imports
from qt_py_convert._modules import psep0101
from qt_py_convert.general import \
    merge_dict, _custom_misplaced_members, _color, AliasDict, _change_verbose

COMMON_MODULES = Qt._common_members.keys() + ["QtCompat"]


def main_handler(msg):
    print("[%s] %s" % (_color(35, "qt_py_convert"), msg))


def atomtrailers_handler(msg):
    print("[%s] %s" % (_color(35, "qt4->qt5"), msg))


def _cleanup_imports(red, aliases, mappings, skip_lineno=False):
    replaced = False
    deletion_index = []
    imps = red.find_all("FromImportNode")
    imps += red.find_all("ImportNode")
    print(_color(34, "==========================="))
    print(_color(34, _color(4, "Consolidating Import lines.")))
    for child in imps:
        for value in child.value:
            if value.value == "Qt":
                if not replaced:
                    names = filter(
                        lambda a: True if a in COMMON_MODULES else False,
                        aliases["used"],
                    )
                    if not names:  # Attempt to build names from input aliases.
                        members = filter(
                            lambda a: True if a in mappings else False,
                            aliases["root_aliases"],
                        )
                        names = []
                        for member in members:
                            names.append(mappings[member].split(".")[0])

                    if not names:
                        print(
                            "%s: %s" % (
                                _color(31, "WARNING"),
                                _color(32, "We have found no usages of Qt in "
                                           "this script despite you previously"
                                           " having imported the binding.\nIf "
                                           "you think this is in error, "
                                           "please let us know and submit an "
                                           "issue ticket with the example you "
                                           "think is wrong.")
                            )
                        )
                        child.parent.remove(child)
                        continue
                    # What we want to replace to.
                    replace_text = "from Qt import {key}".format(
                        key=", ".join(names)
                    )

                    cleaning_message = (
                        "%s imports from: \"{original}\" to \"{replacement}\""
                        % _color(32, "Cleaning")
                    )
                    _change_verbose(
                        msg=cleaning_message,
                        handler=main_handler,
                        node=child,
                        replacement=replace_text,
                        skip_lineno=skip_lineno,
                    )

                    child.replace(replace_text)
                    replaced = True
                else:
                    deleting_message = (
                        "%s \"{original}\"" % _color(31, "Deleting")
                    )
                    _change_verbose(
                        msg=deleting_message,
                        handler=main_handler,
                        node=child,
                        replacement="",
                        skip_lineno=skip_lineno,
                    )
                    child.parent.remove(child)
            else:
                pass
    for child in reversed(deletion_index):
        print("Deleting %s" % child)
        child.parent.remove(child)
        # red.remove(child)


def _convert_attributes(red, aliases, skip_lineno=False):
    # Compile our expressions
    expressions = [
        (
            re.compile(
                r"^(?P<module>{modules})\.(?P<widget>(?:{widgets})(?:[\.\[\(].*)?)$".format(             # Regular expression
                    modules="|".join(re.escape(name) for name in Qt._common_members.keys()),
                    widgets="|".join(re.escape(widget) for widget in Qt._common_members[module_name])
                ),
                re.MULTILINE
            ),
            module_name
        )
        for module_name in Qt._common_members
    ]

    def finder_function_factory(exprs):
        def finder_function(value):
            return any([
                expression.match(value.dumps()) for expression, mod in exprs
            ])
        return finder_function

    mappings = {}
    # Find any AtomTrailersNode that matches any of our expressions.
    nodes = red.find_all(
        "AtomTrailersNode",
        value=finder_function_factory(expressions)
    )
    nodes += red.find_all(
        "DottedNameNode",
        value=finder_function_factory(expressions)
    )
    header_written = False
    for node in nodes:
        orig_node_str = node.dumps()
        added_module = False
        for expr, module_ in expressions:
            modified = expr.sub(
                r"{module}.\2".format(module=module_),
                orig_node_str,
            )

            if modified != orig_node_str:
                mappings[orig_node_str] = modified
                aliases["used"].add(module_)
                added_module = True
                if not header_written:
                    print(_color(33, "========================="))
                    print(_color(33, _color(4, "Parsing AtomTrailersNodes")))
                    header_written = True

                _change_verbose(
                    handler=atomtrailers_handler,
                    node=node,
                    replacement=modified,
                    skip_lineno=skip_lineno,
                )
                node.value[0].replace(module_)
                # node.replace(modified)
                break
        if not added_module:
            aliases["used"].add(orig_node_str.split(".")[0])
    return mappings


def _convert_root_name_imports(red, aliases, mappings, skip_lineno=False):
    """
    _convert_root_name_imports is a function that should be used in cases
    where the original code just imported the python binding and did not
    import any second level modules.

    For example:
    ```
    import PySide

    ```
    :param red:
    :type red:
    :param aliases:
    :type aliases:
    :param mappings:
    :type mappings:
    :return:
    :rtype:
    """
    def filter_function(value):
        return value.dumps().startswith("Qt.")
    matches = red.find_all("AtomTrailersNode", value=filter_function)
    matches += red.find_all("DottedNameNode", value=filter_function)
    L_STRIP_QT_RE = re.compile(r"^Qt\.",)

    if matches:
        print(_color(35, "===================================="))
        print(_color(35, _color(4, "Replacing top level binding imports.")))

    for node in matches:
        name = L_STRIP_QT_RE.sub(
            "", node.dumps(), count=1
        )

        root_name = name.split(".")[0]
        if root_name in COMMON_MODULES:
            aliases["root_aliases"].add(
                root_name
            )
            _change_verbose(
                handler=main_handler,
                node=node,
                replacement=name,
                skip_lineno=skip_lineno,
            )
            node.replace(name)
        else:
            print(
                "Unknown second level module from the Qt package \"%s\""
                % _color(33, root_name)
            )


def _convert_body(red, aliases, mappings, skip_lineno=False):
    def expression_factory(expr_key):
        regex = re.compile(
            r"{value}(?:[\.\[\(].*)?$".format(value=expr_key),
            re.DOTALL
        )

        def expression_filter(value):
            return regex.match(value.dumps())

        return expression_filter

    # Body of the function
    for key in sorted(mappings, key=len):
        print(_color(36, "-"*len(key)))
        print(_color(36, _color(4, key)))
        if "." in key:
            filter_function = expression_factory(key)
            matches = red.find_all("AtomTrailersNode", value=filter_function)
            matches += red.find_all("DottedNameNode", value=filter_function)
        else:
            matches = red.find_all("NameNode", value=key)
        if matches:
            for node in matches:
                # Dont replace imports, we already did that.
                if not node.parent_find("ImportNode") and not node.parent_find("FromImportNode"):
                    # If the node's parent has dot syntax. Make sure we are the first one.
                    # Reasoning: We are relying on namespacing, so we don't want to turn bob.foo.cat into bob.foo.bear.
                    #            Because bob.foo.cat might not be equal to the mike.cat that we meant to change.
                    if node.parent.type == "atomtrailers" and not node.parent.value[0] == node:
                        continue

                    replacement = node.dumps().replace(key, mappings[key])
                    _change_verbose(
                        handler=main_handler,
                        node=node,
                        replacement=replacement,
                        skip_lineno=skip_lineno,
                    )
                    if mappings[key].split(".")[0] in COMMON_MODULES:
                        aliases["used"].add(mappings[key].split(".")[0])

                    node.replace(replacement)
                    # match.replace(mappings[key])


def _convert_mappings(aliases, mappings):
    core_expr, gui_expr, widgets_expr = [
        re.compile(
            r"(?P<module>{modules})\.(?P<widget>{widgets})".format(
                # Regular expression
                modules="|".join(
                    re.escape(name) for name in Qt._common_members.keys()
                ),
                widgets="|".join(
                    re.escape(widget) for widget in Qt._common_members[module_name]
                )
            )
        )
        for module_name in ["QtCore", "QtGui", "QtWidgets"]
    ]
    for from_mapping in mappings:
        for module_name, expression in [("QtCore", core_expr),
                                        ("QtGui", gui_expr),
                                        ("QtWidgets", widgets_expr)]:
            modified_mapping = expression.sub(
                r"{module}.\2".format(module=module_name),
                mappings[from_mapping]
            )
            if modified_mapping != mappings[from_mapping]:
                # Mapping changed
                aliases["used"].add(module_name)
                mappings[from_mapping] = modified_mapping
    return mappings


def misplaced_members(aliases, mappings):
    members = Qt._misplaced_members.get(Qt.__binding__.lower(), {})
    for binding in aliases["bindings"]:
        if binding.lower() in Qt._misplaced_members:
            print("Merging %s to bindings" % Qt._misplaced_members.get(binding.lower(), {}))
            members.update(Qt._misplaced_members.get(binding.lower(), {}))
        elif binding.lower() in _custom_misplaced_members:
            members.update(_custom_misplaced_members.get(binding.lower(), {}))
        else:
            print("Could not find misplaced members for %s" % binding.lower())

        _msg = "Replacing \"{original}\" with \"{replacement}\" in mappings"
        if members:
            for source in members:
                replaced = False
                dest = members[source]
                if isinstance(dest, (list, tuple)):
                    dest, _ = members[source]
                for current_key in mappings:
                    if mappings[current_key] == source:
                        _change_verbose(
                            msg=_msg,
                            handler=main_handler,
                            node=mappings[current_key],
                            replacement=dest,
                        )
                        mappings[current_key] = dest
                        replaced = True
                if not replaced:
                    print("Adding %s in mappings" % dest)
                    mappings[source] = dest
    return aliases, mappings


def run(text, skip_lineno=False):
    AliasDict.clean()
    try:
        red = redbaron.RedBaron(text)
    except Exception as err:
        print(str(err))
        traceback.print_exc()
        return AliasDict, {}, text

    from_a, from_m = from_imports.process(red, skip_lineno=skip_lineno)
    import_a, import_m = imports.process(red, skip_lineno=skip_lineno)
    mappings = merge_dict(from_m, import_m, keys_both=True)
    aliases = merge_dict(from_a, import_a, keys=["bindings", "root_aliases"])

    aliases, mappings = misplaced_members(aliases, mappings)
    aliases["used"] = set()

    mappings = _convert_mappings(aliases, mappings)

    # Convert using the psep0101 module.
    psep0101.process(red, skip_lineno=skip_lineno)
    _convert_body(red, aliases, mappings, skip_lineno=skip_lineno)
    _convert_root_name_imports(red, aliases, mappings, skip_lineno=skip_lineno)
    _convert_attributes(red, aliases, skip_lineno=skip_lineno)
    if aliases["root_aliases"]:
        _cleanup_imports(red, aliases, mappings, skip_lineno=skip_lineno)

    # Done!
    dumps = red.dumps()
    # print(_color(32, "The following is the modified script:"))
    # print(_color(34, dumps))
    return aliases, mappings, dumps


def _is_py(path):
    if path.endswith(".py"):
        return True
    elif not os.path.splitext(path)[1] and os.path.isfile(path):
        with open(path, "rb") as fh:
            if "python" in fh.read(1024):
                return True
    return False


def process_file(fp, write=False, skip_lineno=False):
    if not _is_py(fp):
        print(
            "\tSkipping \"%s\"... It does not appear to be a python file." % fp
        )
        return
    with open(fp, "rb") as fh:
        source = fh.read()

    print("Processing %s" % fp)
    try:
        aliases, mappings, modified_code = run(source, skip_lineno=skip_lineno)
        pprint(aliases)
        pprint(mappings)
        if write:
            print("Writing modified code to %s" % fp)
            with open(fp, "wb") as fh:
                fh.write(modified_code)
    except:
        print("ERROR: Error processing file: \"%s\"" % fp)
        traceback.print_exc()


def process_folder(folder, recursive=False, write=False, skip_lineno=False):

    def _is_dir(path):
        return True if os.path.isdir(os.path.join(folder, path)) else False

    # TODO: Might need to parse the text to remove whitespace at the EOL.
    #       #101 at https://github.com/PyCQA/baron documents this issue.

    for fn in filter(_is_py, os.listdir(folder)):
        process_file(
            os.path.join(folder, fn), write=write, skip_lineno=skip_lineno
        )
        print("-" * 50)

    if not recursive:
        return

    for fn in filter(_is_dir, os.listdir(folder)):
        process_folder(
            os.path.join(folder, fn),
            recursive=recursive,
            write=write,
            skip_lineno=skip_lineno
        )


if __name__ == "__main__":
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/assetbrowser/trunk/src/python/assetbrowser/workflow/widgets/custom.py", write=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/assetbrowser/trunk/src/python/assetbrowser/widget/Columns.py", write=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ddg/trunk/src/python", recursive=True, write=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ddqt/trunk/src/python", recursive=True, write=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/nukepipeline/branches/nukepipeline_5/src/nuke/nodes/nukepipeline/ShotLook/shot_look.py", write=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/lightpipeline/trunk/src/python/lightpipeline/ui", recursive=True, write=True, fast_exit=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/lightpipeline/trunk/src/python/lightpipeline/ui/errorDialogUI.py", write=True, fast_exit=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/lightpipeline/trunk/src/python/lightpipeline/ui/HDRWidgetComponents.py", write=True, fast_exit=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/nukepipeline/branches/nukepipeline_5/src/", recursive=True, write=True, fast_exit=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/assetbrowser/trunk/src", recursive=True, write=True)
    # folder = os.path.abspath("../../../../tests/sources")
    # process_folder(folder, recursive=True, write=True)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/shooter/branches/predefined_notes_branch/src", recursive=True, write=True)
    process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/texturepipeline/trunk/src/python/texturepipeline/utils/level.py", write=False, skip_lineno=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ticket/trunk/src/python/ticket/flaregun_ui.py", write=True, fast_exit=False)
