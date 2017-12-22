import os
from pprint import pprint
import re
import traceback


from qt_py_convert.external import Qt
from qt_py_convert.external import redbaron

from qt_py_convert._modules import from_imports
from qt_py_convert._modules import imports
from qt_py_convert._modules import psep0101
from qt_py_convert.general import merge_dict, _custom_misplaced_members, \
    _color, AliasDict, _change_verbose, UserInputRequiredException, ErrorClass

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

                # Hacky message creation for better logging.
                # This allows us to highlight exactly which part of the
                # statement is being replaced.
                original_part = _color(1, str(node.value[0]).strip("\n"))
                original_rest = _color(37, "." + ".".join([
                        str(n).strip("\n")
                        for n in node.value[1:]
                ]))
                replacement_part = _color(1, module_)
                replacement_rest = _color(37, "." + ".".join([
                        str(n).strip("\n")
                        for n in node.value[1:]
                    ]))
                msg = "Replacing \"{original}\" with \"{replacement}\"".format(
                    original=original_part + original_rest,
                    replacement=replacement_part + replacement_rest,
                )
                _change_verbose(
                    handler=atomtrailers_handler,
                    node=node.value[0],
                    replacement=module_,
                    skip_lineno=skip_lineno,
                    msg=msg
                )
                # Only replace the first node part of the statement.
                # This allows us to keep any child nodes that have already
                # been gathered attached to the main node tree.

                # This was the cause of a bug in our internal code.
                # http://dd-git.d2.com/ahughes/qt_py_convert/issues/19

                # A node that had child nodes that needed replacements on the
                # same line would cause an issue if we replaced the entire
                # line the first replacement. The other replacements on that
                # line would not stick because they would be replacing to an
                # orphaned tree.
                node.value[0].replace(module_)
                break
            else:
                if orig_node_str.split(".")[0] in COMMON_MODULES:
                    aliases["used"].add(orig_node_str.split(".")[0])
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
    """
    _convert_body is  one of the first conversion functions to run on the
    redbaron ast.
    It finds the NameNode's or the AtomTrailersNode+DottedNameNodes and will
    run them through the filter expressions built off of the values in
    mappings.
    If found, it will replace the source value with the destination value in
    mappings.

    :param red: The redbaron ast.
    :type red: redbaron.RedBaron
    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param mappings: Mappings is information about the bindings that are used.
    :type mappings: dict
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    """
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
                parent_is_import = node.parent_find("ImportNode")
                parent_is_fimport = node.parent_find("FromImportNode")
                if not parent_is_import and not parent_is_fimport:
                    # If the node's parent has dot syntax. Make sure we are
                    # the first one. Reasoning: We are relying on namespacing,
                    # so we don't want to turn bob.foo.cat into bob.foo.bear.
                    # Because bob.foo.cat might not be equal to the mike.cat
                    # that we meant to change.
                    if node.parent.type == "atomtrailers":
                        if not node.parent.value[0] == node:
                            continue

                    if node.dumps().split(".")[0] in COMMON_MODULES:
                        aliases["used"].add(node.dumps().split(".")[0])
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
    """
    _convert_mappings will build a proper mapping dictionary using any
    aliases that we have discovered previously.
    It builds regular expressions based off of the Qt._common_members and will
    replace the mappings that are used with updated ones in Qt.py

    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param mappings: Mappings is information about the bindings that are used.
    :type mappings: dict
    :return: _convert_mappings will just return the mappings dict,
        however it is updating the aliases["used"] set.
    :rtype: dict
    """
    expressions = [
        re.compile(
            r"(?P<module>{modules})\.(?P<widget>{widgets})$".format(
                # Regular expression
                modules="|".join(
                    re.escape(name) for name in Qt._common_members.keys()
                ),
                widgets="|".join(
                    re.escape(widget) for widget in Qt._common_members[module]
                )
            )
        )
        for module in Qt._common_members.keys()
    ]
    for from_mapping in mappings:
        iterable = zip(Qt._common_members.keys(), expressions)
        for module_name, expression in iterable:
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
    """
    misplaced_members uses the internal "_misplaced_members" from Qt.py as
    well as any "_custom_misplaced_members" that you have set to update the
    detected binding members. The Q.py misplaced memebers aid in updating
    bindings to Qt5 compatible locations.

    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param mappings: Mappings is information about the bindings that are used.
    :type mappings: dict
    :return: A tuple of aliases and mappings that have been updated.
    :rtype: tuple[dict,dict]
    """
    members = Qt._misplaced_members.get(Qt.__binding__.lower(), {})
    for binding in aliases["bindings"]:
        if binding in Qt._misplaced_members:
            print("Merging %s to bindings" % Qt._misplaced_members.get(binding, {}))
            members.update(Qt._misplaced_members.get(binding, {}))
        elif binding in _custom_misplaced_members:
            members.update(_custom_misplaced_members.get(binding, {}))
        else:
            print("Could not find misplaced members for %s" % binding)

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


def run(text, skip_lineno=False, tometh_flag=False):
    """
    run is the main driver of the file. It takes the text of a file and any
    flags that you want to set.
    It does not deal with any file opening or writting, you must have teh raw
    text already.

    :param text: Text from a python file that you want to process.
    :type text: str
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param tometh_flag: tometh_flag is an optional feature flag. Once turned
        on, it will attempt to replace any QString/QVariant/etc apiv1.0 methods
        that are being used in your script. It is currently not smart enough to
        confirm that you don't have any custom objects with the same method
        signature to PyQt4's apiv1.0 ones.
    :type tometh_flag: bool
    :return: run will return a tuple of runtime information. aliases,
        mappings, and the resulting text. Aliases is the replacement
        information that it built, mappings is information about the bindings
        that were used.
    :rtype: tuple[dict,dict,str]
    """
    AliasDict.clean()
    try:
        red = redbaron.RedBaron(text)
    except Exception as err:
        print(str(err))
        traceback.print_exc()

        d = object()
        setattr(d, "row", 0)
        setattr(d, "row_to", 0)
        setattr(d, "reaspm", traceback.format_exc())
        AliasDict["errors"].add(d)
        return AliasDict, {}, text

    from_a, from_m = from_imports.process(red, skip_lineno=skip_lineno)
    import_a, import_m = imports.process(red, skip_lineno=skip_lineno)
    mappings = merge_dict(from_m, import_m, keys_both=True)
    aliases = merge_dict(from_a, import_a, keys=["bindings", "root_aliases"])

    aliases, mappings = misplaced_members(aliases, mappings)
    aliases["used"] = set()

    mappings = _convert_mappings(aliases, mappings)

    # Convert using the psep0101 module.
    psep0101.process(red, skip_lineno=skip_lineno, tometh_flag=tometh_flag)
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
    """
    My helper method for process_folder to decide if a file is a python file
    or not.
    It is currently checking the file extension and then falling back to
    checking the first line of the file.

    :param path: The filepath to the file that we are querying.
    :type path: str
    :return: True if it's a python file. False otherwise
    :rtype: bool
    """
    if path.endswith(".py"):
        return True
    elif not os.path.splitext(path)[1] and os.path.isfile(path):
        with open(path, "rb") as fh:
            if "python" in fh.readline():
                return True
    return False


def _build_exc(error, line_data):
    """
    raises a UserInputRequiredException from an instance of an ErrorClass.

    :param error: The ErrorClass instance that was created somewhere in
        qt_py_convert.
    :type error: qt_py_convert.general.ErrorClass
    :param line_data: List of lines from the file we are working on.
    :type line_data: List[str...]
    """
    line_no_start = error.row
    line_no_end = error.row_to + 1
    lines = line_data[line_no_start:line_no_end]
    line = "".join(line_data[line_no_start:line_no_end])

    line_no = "Line"
    if len(lines) > 1:
        line_no += "s "
        line_no += "%d-%d" % (line_no_start + 1, line_no_end )
    else:
        line_no += " %d" % (line_no_start + 1)

    template = """
{line_no}
{line}
{reason}
"""
    raise UserInputRequiredException(
        _color(
            31,
            template.format(
                line_no=line_no,
                line=_color(37, line.rstrip("\n")),
                reason=_color(31, error.reason)
            )
        )
    )


def process_file(fp, write=False, skip_lineno=False, tometh_flag=False):
    """
    One of the entry-point functions in qt_py_convert.
    If you are looking to process a single python file, this is your function.

    :param fp: The source file that you want to start processing.
    :type fp: str
    :param write: Should we overwrite the files that we process with their
        fixed versions?
    :type write: bool
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param tometh_flag: tometh_flag is an optional feature flag. Once turned
        on, it will attempt to replace any QString/QVariant/etc apiv1.0 methods
        that are being used in your script. It is currently not smart enough to
        confirm that you don't have any custom objects with the same method
        signature to PyQt4's apiv1.0 ones.
    :type tometh_flag: bool
    """
    if not _is_py(fp):
        print(
            "\tSkipping \"%s\"... It does not appear to be a python file." % fp
        )
        return
    with open(fp, "rb") as fh:
        lines = fh.readlines()
        source = "".join(lines)

    print("Processing %s" % fp)
    try:
        aliases, mappings, modified_code = run(
            source,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag
        )
        pprint(aliases)
        pprint(mappings)
        if write:
            print("Writing modified code to %s" % fp)
            with open(fp, "wb") as fh:
                fh.write(modified_code)
    except BaseException:
        print("ERROR: Error processing file: \"%s\"" % fp)
        traceback.print_exc()

    # Process any errors that may have happened throughout the process.
    if AliasDict["errors"]:
        main_handler(_color(
            31,
            "The Following errors were recovered while converting %s:\n" % fp
        ))
        for error in AliasDict["errors"]:
            try:
                _build_exc(error, lines)
            except UserInputRequiredException as err:
                main_handler(str(err))

def process_folder(folder, recursive=False, write=False, skip_lineno=False, tometh_flag=False):
    """
    One of the entry-point functions in qt_py_convert.
    If you are looking to process every python file in a folder, this is your
    function.

    :param folder: The source folder that you want to start processing the
        python files of.
    :type folder: str
    :param recursive: Do you want to continue recursing through sub-folders?
    :type recursive: bool
    :param write: Should we overwrite the files that we process with their
        fixed versions?
    :type write: bool
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param tometh_flag: tometh_flag is an optional feature flag. Once turned
        on, it will attempt to replace any QString/QVariant/etc apiv1.0 methods
        that are being used in your script. It is currently not smart enough to
        confirm that you don't have any custom objects with the same method
        signature to PyQt4's apiv1.0 ones.
    :type tometh_flag: bool
    """

    def _is_dir(path):
        return True if os.path.isdir(os.path.join(folder, path)) else False

    # TODO: Might need to parse the text to remove whitespace at the EOL.
    #       #101 at https://github.com/PyCQA/baron documents this issue.

    for fn in filter(_is_py, [os.path.join(folder, fp) for fp in os.listdir(folder)]):
        process_file(
            os.path.join(folder, fn),
            write=write,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag
        )
        print("-" * 50)

    if not recursive:
        return

    for fn in filter(_is_dir, os.listdir(folder)):
        process_folder(
            os.path.join(folder, fn),
            recursive=recursive,
            write=write,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag
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
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/rvplugins/tags/0.19.4/src", recursive=True, write=True, skip_lineno=True, tometh_flag=True)
    process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/texturepipeline/branches/qt_py/src/python/texturepipeline/maya/scripts/vrayTEST/fromLightpipeline/ddTextureAssignment/util.py", write=True, skip_lineno=True, tometh_flag=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ticket/trunk/src/python/ticket/flaregun_ui.py", write=True, fast_exit=False)
