# Copyright 2018 Digital Domain 3.0
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
import os
import re
import sys
import traceback


import Qt
if Qt.__version__ < "1.2.0.b2":
    raise ImportError(
        "Improper Qt.py version installed. Qt.py must be version 1.2.0.b2 or above. Version %s installed instead." % Qt.__version__
    )
import redbaron

from qt_py_convert._modules import from_imports
from qt_py_convert._modules import imports
from qt_py_convert._modules import psep0101
from qt_py_convert._modules import unsupported
from qt_py_convert.general import merge_dict, ErrorClass, \
    ALIAS_DICT, change, UserInputRequiredException, ANSI,  \
    __suplimentary_bindings__, is_py, build_exc, WriteFlag
from qt_py_convert.color import color_text
from qt_py_convert.mappings import convert_mappings, misplaced_members
from qt_py_convert.log import get_logger

COMMON_MODULES = list(Qt._common_members.keys()) + ["QtCompat"]


MAIN_LOG = get_logger("run")
Qt4_Qt5_LOG = get_logger("qt4->qt5")


def _cleanup_imports(red, aliases, mappings, skip_lineno=False):
    """
    _cleanup_imports fixes the imports.
    Initially changing them as per the following:
    >>> from PyQt4 import QtGui, QtCore
    to 
    >>> from Qt import QtGui, QtCore
    for each binding.
    It doesn't have enough knowledge of your script at this point to know if 
      you need QtWidgets or if the ones you import are all used. 
    This will get reflected at the end.

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
    replaced = False
    deletion_index = []
    imps = red.find_all("FromImportNode")
    imps += red.find_all("ImportNode")

    MAIN_LOG.debug(color_text(
        text="===========================",
        color=ANSI.colors.blue
    ))
    MAIN_LOG.debug(color_text(
        text="Consolidating Import lines.",
        color=ANSI.colors.blue,
        style=ANSI.styles.underline,
    ))

    for child in imps:
        for value in child.value:
            value_str = value.value
            try:
                value_str = value_str.dumps()
            except AttributeError:
                pass
            if value.value == "Qt" or value_str in __suplimentary_bindings__:
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
                        MAIN_LOG.warning(color_text(
                            text="We have found no usages of Qt in "
                                 "this script despite you previously"
                                 " having imported the binding.\nIf "
                                 "you think this is in error, "
                                 "please let us know and submit an "
                                 "issue ticket with the example you "
                                 "think is wrong.",
                            color=ANSI.colors.green
                        ))
                        child.parent.remove(child)
                        continue
                    # What we want to replace to.
                    replace_text = "from Qt import {key}".format(
                        key=", ".join(names)
                    )

                    cleaning_message = color_text(
                        text="Cleaning", color=ANSI.colors.green
                    )
                    cleaning_message += (
                        " imports from: \"{original}\" to \"{replacement}\""
                    )
                    change(
                        msg=cleaning_message,
                        logger=MAIN_LOG,
                        node=child,
                        replacement=replace_text,
                        skip_lineno=skip_lineno
                    )

                    child.replace(replace_text)
                    replaced = True
                else:
                    deleting_message = "{name} \"{orig}\"".format(
                        orig=str(child).strip("\n"),
                        name=color_text(text="Deleting", color=ANSI.colors.red)
                    )
                    change(
                        msg=deleting_message,
                        logger=MAIN_LOG,
                        node=child,
                        replacement="",
                        skip_lineno=skip_lineno
                    )
                    child.parent.remove(child)
            else:
                pass
    for child in reversed(deletion_index):
        MAIN_LOG.debug("Deleting {node}".format(node=child))
        child.parent.remove(child)
        # red.remove(child)


def _convert_attributes(red, aliases, skip_lineno=False):
    """
    _convert_attributes converts all AtomTrailersNodes and DottenNameNodes to 
      the Qt5/PySide2 api matching Qt.py..
    This means that anything that was using QtGui but is now using QtWidgets 
      will be updated for example.
    It does not do any api v1 - api v2 conversion or specific 
      misplaced_mapping changes.

    :param red: The redbaron ast.
    :type red: redbaron.RedBaron
    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    """
    # Compile our expressions
    # Our expressions are basically as follows:
    # From:
    #   <Any Qt SLM>.<any_member of A>
    # To:
    #   <A>.<\back reference to the member matched>
    # Where A is the specific Qt SecondLevelModule that we are building this 
    #   expression for.
    # 
    # Also sorry this is longer than 79 chars..
    # It gets harder to read the more I try to make it more readable.
    expressions = [
        (
            re.compile(
                r"^(?P<module>{modules})\.(?P<widget>(?:{widgets})(?:[.\[(].*)?)$".format(             # Regular expression
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
        """Basic function factory. Used as a find_all delegate for red."""
        def finder_function(value):
            """The filter for our red.find_all function."""
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
                    MAIN_LOG.debug(color_text(
                        text="=========================",
                        color=ANSI.colors.orange,
                    ))
                    MAIN_LOG.debug(color_text(
                        text="Parsing AtomTrailersNodes",
                        color=ANSI.colors.orange,
                        style=ANSI.styles.underline
                    ))
                    header_written = True

                repl = str(node).replace(
                    str(node.value[0]).strip("\n"), 
                    module_
                )

                change(
                    logger=Qt4_Qt5_LOG,
                    node=node,
                    replacement=repl,
                    skip_lineno=skip_lineno
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
            # else:
            #     if orig_node_str.split(".")[0] in COMMON_MODULES:
            #         aliases["used"].add(orig_node_str.split(".")[0])
        if not added_module:
            aliases["used"].add(orig_node_str.split(".")[0])
    return mappings


def _convert_root_name_imports(red, aliases, skip_lineno=False):
    """
    _convert_root_name_imports is a function that should be used in cases
    where the original code just imported the python binding and did not
    import any second level modules.

    For example:
    ```
    import PySide

    ```
    :param red: The redbaron ast.
    :type red: redbaron.RedBaron
    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    """
    def filter_function(value):
        """A filter delegate for our red.find_all function."""
        return value.dumps().startswith("Qt.")
    matches = red.find_all("AtomTrailersNode", value=filter_function)
    matches += red.find_all("DottedNameNode", value=filter_function)
    lstrip_qt_regex = re.compile(r"^Qt\.",)

    if matches:
        MAIN_LOG.debug(color_text(
            text="====================================",
            color=ANSI.colors.purple,
        ))
        MAIN_LOG.debug(color_text(
            text="Replacing top level binding imports.",
            color=ANSI.colors.purple,
            style=ANSI.styles.underline,
        ))

    for node in matches:
        name = lstrip_qt_regex.sub(
            "", node.dumps(), count=1
        )

        root_name = name.split(".")[0]
        if root_name in COMMON_MODULES:
            aliases["root_aliases"].add(
                root_name
            )
            change(
                logger=MAIN_LOG,
                node=node,
                replacement=name,
                skip_lineno=skip_lineno
            )
            node.replace(name)
        else:
            MAIN_LOG.warning(
                "Unknown second level module from the Qt package \"{}\""
                .format(
                    color_text(text=root_name, color=ANSI.colors.orange)
                )
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
        """
        expression_factory is a function factory for building a regex.match
        function for a specific key that we found in misplaced_mappings
        """
        regex = re.compile(
            r"{value}(?:[\.\[\(].*)?$".format(value=expr_key),
            re.DOTALL
        )

        def expression_filter(value):
            """
            Basic filter function matching for red.find_all against a regex
            previously created from the factory
            ."""
            return regex.match(value.dumps())

        return expression_filter

    # Body of the function
    for key in sorted(mappings, key=len):
        MAIN_LOG.debug(color_text(
            text="-"*len(key),
            color=ANSI.colors.teal,
        ))
        MAIN_LOG.debug(color_text(
            text=key,
            color=ANSI.colors.teal,
            style=ANSI.styles.underline,
        ))
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
                    if hasattr(node.parent, "type") and node.parent.type == "atomtrailers":
                        if not node.parent.value[0] == node:
                            continue

                    if key != mappings[key]:
                        replacement = node.dumps().replace(key, mappings[key])
                        change(
                            logger=MAIN_LOG,
                            node=node,
                            replacement=replacement,
                            skip_lineno=skip_lineno
                        )
                        if mappings[key].split(".")[0] in COMMON_MODULES:
                            aliases["used"].add(mappings[key].split(".")[0])

                        node.replace(replacement)
                    else:
                        if node.dumps().split(".")[0] in COMMON_MODULES:
                            aliases["used"].add(node.dumps().split(".")[0])
                    # match.replace(mappings[key])


def run(text, skip_lineno=False, tometh_flag=False, explicit_signals_flag=False):
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
    ALIAS_DICT.clean()
    try:
        red = redbaron.RedBaron(text)
    except Exception as err:
        MAIN_LOG.critical(str(err))
        traceback.print_exc()

        ErrorClass(row_from=0, row_to=0, reason=traceback.format_exc())
        return ALIAS_DICT, {}, text

    from_a, from_m = from_imports.process(red, skip_lineno=skip_lineno)
    import_a, import_m = imports.process(red, skip_lineno=skip_lineno)
    mappings = merge_dict(from_m, import_m, keys_both=True)
    aliases = merge_dict(from_a, import_a, keys=["bindings", "root_aliases"])

    aliases, mappings = misplaced_members(aliases, mappings)
    aliases["used"] = set()

    mappings = convert_mappings(aliases, mappings)

    # Convert using the psep0101 module.
    psep0101.process(
        red,
        skip_lineno=skip_lineno,
        tometh_flag=tometh_flag,
        explicit_signals_flag=explicit_signals_flag
    )
    _convert_body(red, aliases, mappings, skip_lineno=skip_lineno)
    _convert_root_name_imports(red, aliases, skip_lineno=skip_lineno)
    _convert_attributes(red, aliases, skip_lineno=skip_lineno)
    if aliases["root_aliases"]:
        _cleanup_imports(red, aliases, mappings, skip_lineno=skip_lineno)

    # Build errors from our unsupported module.
    unsupported.process(red, skip_lineno=skip_lineno)

    # Done!
    dumps = red.dumps()
    return aliases, mappings, dumps


def process_file(fp, write_mode=None, path=None, backup=False, skip_lineno=False, tometh_flag=False, explicit_signals_flag=False):
    """
    One of the entry-point functions in qt_py_convert.
    If you are looking to process a single python file, this is your function.

    :param fp: The source file that you want to start processing.
    :type fp: str
    :param write_mode: The type of writing that we are doing.
    :type write_mode: int
    :param path: If passed, it will signify that we are not overwriting.
        It will be a tuple of (src_root, dst_roo)
    :type path: tuple[str,str]
    :param backup: If passed we will create a ".bak" file beside the newly
        created file. The .bak will contain the original source code.
    :type path: bool
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
    if not is_py(fp):
        MAIN_LOG.debug(
            "\tSkipping \"{fp}\"... It does not appear to be a python file."
            .format(fp=fp)
        )
        return
    with open(fp, "rb") as fh:
        lines = fh.readlines()
        source = "".join(lines)

    MAIN_LOG.info("{line}\nProcessing {path}".format(path=fp, line="-"*50))
    try:
        aliases, mappings, modified_code = run(
            source,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag,
            explicit_signals_flag=explicit_signals_flag
        )
        if aliases["used"] or modified_code != source:
            write_path = fp
            if write_mode & WriteFlag.WRITE_TO_STDOUT:
                sys.stdout.write(modified_code)
            else:
                if path and path[0]:  # We are writing elsewhere than the source.
                    src_root, dst_root = path
                    root_relative = fp.replace(src_root, "").lstrip("/")
                    write_path = os.path.join(dst_root, root_relative)

                if backup:  # We are creating a source backup beside the output
                    bak_path = os.path.join(
                        os.path.dirname(write_path),
                        "." + os.path.basename(write_path) + ".bak"
                    )
                    MAIN_LOG.info("Backing up original code to {path}".format(
                        path=bak_path
                    ))
                    with open(bak_path, "wb") as fh:
                        fh.write(source)

                # Write to file. If path is None, we are overwriting.
                MAIN_LOG.info("Writing modifed code to {path}".format(
                    path=write_path)
                )

                if not os.path.exists(os.path.dirname(write_path)):
                    os.makedirs(os.path.dirname(write_path))
                with open(write_path, "wb") as fh:
                    fh.write(modified_code)

    except BaseException:
        MAIN_LOG.critical("Error processing file: \"{path}\"".format(path=fp))
        traceback.print_exc()

    # Process any errors that may have happened throughout the process.
    if ALIAS_DICT["errors"]:
        MAIN_LOG.error(color_text(
            text="The following errors were recovered from {}:\n".format(fp),
            color=ANSI.colors.red,
        ))
        for error in ALIAS_DICT["errors"]:
            try:
                build_exc(error, lines)
            except UserInputRequiredException as err:
                MAIN_LOG.error(str(err))


def process_folder(folder, recursive=False, write_mode=None, path=None, backup=False, skip_lineno=False, tometh_flag=False, explicit_signals_flag=False):
    """
    One of the entry-point functions in qt_py_convert.
    If you are looking to process every python file in a folder, this is your
    function.

    :param folder: The source folder that you want to start processing the
        python files of.
    :type folder: str
    :param recursive: Do you want to continue recursing through sub-folders?
    :type recursive: bool
    :param write_mode: The type of writing that we are doing.
    :type write_mode: int
    :param path: If passed, it will signify that we are not overwriting.
        It will be a tuple of (src_root, dst_roo)
    :type path: tuple[str,str]
    :param backup: If passed we will create a ".bak" file beside the newly
        created file. The .bak will contain the original source code.
    :type path: bool
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

    for fn in filter(is_py, [os.path.join(folder, fp) for fp in os.listdir(folder)]):
        process_file(
            fn,
            write_mode=write_mode,
            path=path,
            backup=backup,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag,
            explicit_signals_flag=explicit_signals_flag
        )
        MAIN_LOG.debug(color_text(text="-" * 50, color=ANSI.colors.black))

    if not recursive:
        return

    for fn in filter(_is_dir, os.listdir(folder)):
        process_folder(
            os.path.join(folder, fn),
            recursive=recursive,
            write_mode=write_mode,
            path=path,
            backup=backup,
            skip_lineno=skip_lineno,
            tometh_flag=tometh_flag,
            explicit_signals_flag=explicit_signals_flag
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
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ddqt/trunk/src/python/ddqt", recursive=True, write=False, skip_lineno=True, tometh_flag=True)
    # folder = os.path.abspath("../../../../tests/sources")
    # process_folder(folder, recursive=True, write=True)
    process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/jstemplate_explorer/branches/qt_compat/src/bin", recursive=True, write_mode=WriteFlag.WRITE_TO_FILE, skip_lineno=True, tometh_flag=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/refchef/branches/qt_compat/src/python/refchef/tagspanel.py", write_mode=WriteFlag.WRITE_TO_FILE, tometh_flag=True, explicit_signals_flag=False)
    # process_folder("/dd/shows/DEVTD/user/work.ahughes/svn/packages/refchef/branches/qt_compat/src/", write_mode=WriteFlag.WRITE_TO_FILE, tometh_flag=True, recursive=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ddqt/trunk/src/python/ddqt/gui/SnapshotModel.py", write=False, tometh_flag=True)
