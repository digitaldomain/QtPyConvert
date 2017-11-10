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
    merge_dict, _custom_misplaced_members, _color, AliasDict

COMMON_MODULES = Qt._common_members.keys() + ["QtCompat"]


def _cleanup_imports(red, aliases, mappings):
    replaced = False
    deletion_index = []
    imps = red.find_all("FromImportNode")
    imps += red.find_all("ImportNode")
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
                    print(
                        "Cleaning imports from: \"%s\" to \"%s\"" % (
                            str(child).strip("\n"), replace_text
                        )
                    )
                    child.replace(replace_text)
                    replaced = True
                else:
                    print("Deleting %s" % child)
                    child.parent.remove(child)
            else:
                pass
    for child in reversed(deletion_index):
        print("Deleting %s" % child)
        child.parent.remove(child)
        # red.remove(child)


def _convert_attributes(red, aliases):
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
    if nodes:
        print("***")
        print(_color(33, "Parsing AtomTrailersNodes"))
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
                print("Replacing %s with %s at line %d" % (
                    str(orig_node_str).strip("\n"),
                    _color(37, modified),
                    node.absolute_bounding_box.top_left.line-1
                ))
                node.value[0].replace(module_)
                # node.replace(modified)
                break
        if not added_module:
            aliases["used"].add(orig_node_str.split(".")[0])
    return mappings


def _convert_body(red, aliases, mappings):
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
        print("***")
        print(_color(36, key))
        if "." in key:
            filter_function = expression_factory(key)
            matches = red.find_all("AtomTrailersNode", value=filter_function)
            matches += red.find_all("DottedNameNode", value=filter_function)
        else:
            matches = red.find_all("NameNode", value=key)
        if matches:
            for match in matches:
                # Dont replace imports, we already did that.
                if not match.parent_find("ImportNode") and not match.parent_find("FromImportNode"):
                    # If the node's parent has dot syntax. Make sure we are the first one.
                    # Reasoning: We are relying on namespacing, so we don't want to turn bob.foo.cat into bob.foo.bear.
                    #            Because bob.foo.cat might not be equal to the mike.cat that we meant to change.
                    if match.parent.type == "atomtrailers" and not match.parent.value[0] == match:
                        continue

                    print("Replacing %s with %s at line %d" % (
                        _color(37, str(match).strip("\n")),
                        _color(37, match.dumps().replace(key, mappings[key])),
                        match.absolute_bounding_box.top_left.line-1
                    ))
                    if mappings[key].split(".")[0] in COMMON_MODULES:
                        aliases["used"].add(mappings[key].split(".")[0])
                    match.replace(match.dumps().replace(key, mappings[key]))
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

        if members:
            for source in members:
                replaced = False
                dest = members[source]
                if isinstance(dest, (list, tuple)):
                    dest, _ = members[source]
                for current_key in mappings:
                    if mappings[current_key] == source:
                        print("Replacing %s with %s in mappings" % (mappings[current_key], dest))
                        mappings[current_key] = dest
                        replaced = True
                if not replaced:
                    print("Adding %s in mappings" % dest)
                    mappings[source] = dest
    return aliases, mappings


def run(text, fast_exit=False):
    try:
        red = redbaron.RedBaron(text)
    except Exception as err:
        print(str(err))
        traceback.print_exc()
        return AliasDict, {}, text

    from_a, from_m = from_imports.process(red)
    import_a, import_m = imports.process(red)
    if fast_exit:
        if from_a == AliasDict and import_a == AliasDict:
            if not from_m and not import_m:
                return AliasDict, {}, text
    mappings = merge_dict(from_m, import_m, keys_both=True)
    aliases = merge_dict(from_a, import_a, keys=["bindings", "root_aliases"])

    aliases, mappings = misplaced_members(aliases, mappings)
    aliases["used"] = set()

    mappings = _convert_mappings(aliases, mappings)

    # Convert using the psep0101 module.
    psep0101.process(red)
    _convert_body(red, aliases, mappings)
    _convert_attributes(red, aliases)
    if aliases["root_aliases"]:
        _cleanup_imports(red, aliases, mappings)

    # Done!
    dumps = red.dumps()
    # print(_color(32, "The following is the modified script:"))
    # print(_color(34, dumps))
    return aliases, mappings, dumps


def process_file(fp, write=False, fast_exit=False):
    with open(fp, "rb") as fh:
        source = fh.read()

    print("Processing %s" % fp)
    aliases, mappings, modified_code = run(source, fast_exit=fast_exit)
    pprint(aliases)
    pprint(mappings)
    if write:
        print("Writing modified code to %s" % fp)
        with open(fp, "wb") as fh:
            fh.write(modified_code)


def process_folder(folder, recursive=False, write=False, fast_exit=False):
    def _get_py(path):
        return True if path.endswith(".py") else False

    def _is_dir(path):
        return True if os.path.isdir(os.path.join(folder, path)) else False

    # TODO: Might need to parse the text to remove whitespace at the EOL.
    #       #101 at https://github.com/PyCQA/baron documents this issue.
    for fn in filter(_get_py, os.listdir(folder)):
        process_file(
            os.path.join(folder, fn), write=write, fast_exit=fast_exit
        )
        print("-" * 50)

    if not recursive:
        return

    for fn in filter(_is_dir, os.listdir(folder)):
        process_folder(os.path.join(folder, fn), recursive, write, fast_exit)


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
    process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/texturepipeline/trunk/src/python/texturepipeline/mari/ddscripts/addChannel.py", write=True)
    # process_file("/dd/shows/DEVTD/user/work.ahughes/svn/packages/ticket/trunk/src/python/ticket/flaregun_ui.py", write=True, fast_exit=False)
