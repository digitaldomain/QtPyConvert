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
"""
The imports module is designed to fix the import statements.
"""
from qt_py_convert.general import __supported_bindings__, ALIAS_DICT, change, \
    supported_binding
from qt_py_convert.log import get_logger

IMPORTS_LOG = get_logger("imports")


class Processes(object):
    """Processes class for import"""
    @staticmethod
    def _build_child_name(child):
        return ".".join([child_part.dumps() for child_part in child.value])

    @staticmethod
    def _no_second_level_module(node, _child_parts, skip_lineno=False):
        replacement = "import Qt"
        change(
            logger=IMPORTS_LOG,
            node=node,
            replacement=replacement,
            skip_lineno=skip_lineno
        )
        node.replace(replacement)

    @classmethod
    def _process_import(cls, red, objects, skip_lineno=False):
        """
        _process_import is designed to replace import methods.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param objects: List of redbaron nodes that matched for this proc.
        :type objects: list
        :param skip_lineno: Global "skip_lineno" flag.
        :type skip_lineno: bool
        """
        binding_aliases = ALIAS_DICT
        mappings = {}

        # Replace each node
        for node, binding in objects:
            for child_index, child in enumerate(node):
                _child_name = cls._build_child_name(child)
                _child_as_name = child.target
                if _child_name.split(".")[0] not in __supported_bindings__ \
                        and _child_as_name not in __supported_bindings__:
                    # Only one of our multi import node's children is relevant.
                    continue

                _child_parts = _child_name.replace(binding, "")
                _child_parts = _child_parts.lstrip(".").split(".")

                # Check to see if there is a second level module
                if len(_child_parts) and _child_parts[0]:
                    second_level_module = _child_parts[0]
                else:
                    if len(node) == 1:
                        # Only one in the import: "import PySide"
                        cls._no_second_level_module(node.parent, _child_parts)
                    else:
                        # Multiple in the import: "import PySide, os"
                        node_parent = node.parent
                        node.pop(child_index)
                        repl = node.parent.dumps() + "\nimport Qt"

                        change(
                            logger=IMPORTS_LOG,
                            node=node_parent,
                            replacement=repl,
                            skip_lineno=skip_lineno
                        )

                        node.parent.replace(repl)
                    if _child_as_name:
                        mappings[_child_as_name] = "Qt"
                    else:
                        mappings[_child_name] = "Qt"
                        binding_aliases["bindings"].add(binding)
                    continue

                mappings[_child_as_name or _child_name] = ".".join(
                    _child_parts
                )

                change(
                    logger=IMPORTS_LOG,
                    node=node.parent,
                    replacement="from Qt import {key}".format(
                        key=second_level_module
                    ),
                    skip_lineno=skip_lineno
                )

                node.parent.replace(
                    "from Qt import {key}".format(key=second_level_module)
                )
                binding_aliases["bindings"].add(binding)
                binding_aliases["root_aliases"].add(second_level_module)
                if binding not in binding_aliases:
                    binding_aliases[binding] = set()
                binding_aliases[binding].add(second_level_module)
        return binding_aliases, mappings

    IMPORT_STR = "IMPORT"
    IMPORT = _process_import


def import_process(store):
    """
    import_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will filter them out if they match something that
        has changed in psep0101
        """
        _raw_module = value.dumps().split(".")[0]
        # See if that import is in our __supported_bindings__
        matched_binding = supported_binding(_raw_module)
        if matched_binding:
            store[Processes.IMPORT_STR].add(
                    (value, matched_binding)
            )
            return True
    return filter_function


def process(red, skip_lineno=False, **kwargs):
    """
    process is the main function for the import process.

    :param red: Redbaron ast.
    :type red: redbaron.redbaron
    :param skip_lineno: An optional performance flag. By default, when the
        script replaces something, it will tell you which line it is
        replacing on. This can be useful for tracking the places that
        changes occurred. When you turn this flag on however, it will not
        show the line numbers. This can give great performance increases
        because redbaron has trouble calculating the line number sometimes.
    :type skip_lineno: bool
    :param kwargs: Any other kwargs will be ignored.
    :type kwargs: dict
    """
    issues = {
        Processes.IMPORT_STR: set(),
    }
    red.find_all("ImportNode", value=import_process(issues))
    key = Processes.IMPORT_STR

    if issues[key]:
        return getattr(Processes, key)(red, issues[key], skip_lineno=skip_lineno)
    else:
        return ALIAS_DICT, {}
