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
import re

from qt_py_convert.general import ALIAS_DICT, ErrorClass


class Processes(object):

    @staticmethod
    def _process_load_ui_type(red, objects, skip_lineno=False):
        for node in objects:
            ErrorClass.from_node(
                node=node,
                reason="""
    The Qt.py module does not support uic.loadUiType as it is not a method in PySide.
    Please see: https://github.com/mottosso/Qt.py/issues/237
        For more information. 

    This will break and you will have to update this or refactor it out."""
            )

    LOADUITYPE_STR = "LOADUITYPE"
    LOADUITYPE = _process_load_ui_type


def unsupported_process(store):
    """
    unsupported_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    _loaduitype_expression = re.compile(
        r"(?:uic\.)?loadUiType", re.DOTALL
    )

    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will
        filter them out if they match something that is unsupported in Qt.py
        """
        found = False
        if _loaduitype_expression.search(value.dumps()):
            store[Processes.LOADUITYPE_STR].add(value)
            found = True
        if found:
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
        Processes.LOADUITYPE_STR: set(),
    }

    red.find_all("AtomTrailersNode", value=unsupported_process(issues))
    red.find_all("DottedNameNode", value=unsupported_process(issues))
    key = Processes.LOADUITYPE_STR

    if issues[key]:
        return getattr(Processes, key)(red, issues[key],
                                       skip_lineno=skip_lineno)
    else:
        return ALIAS_DICT, {}
