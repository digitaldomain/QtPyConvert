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


def to_methods(function_str):
    """
    to_methods is a helper function that aims to replace all the "toX" methods
    from PyQt4-apiV1.0.

    :param function_str: String that represents something that may have the
        toX methods in it.
    :type function_str: str
    :return: A string that, if a method was found, has been cleaned.
    :rtype: str
    """
    match = re.match(
        r"""
(?P<object>.*?)                                       # Whatever was before it.
\.to(?:                                               # Get all the options of.
    String|                                           # toString
    Int|                                              # toInt
    Float|                                            # toFloat
    Bool|                                             # toBool
    PyObject|                                         # toPyObject
    Ascii                                             # toAscii
)\(.*?\)(?P<end>.*)""",
        function_str,
        re.VERBOSE | re.MULTILINE
    )
    if match:
        replacement = match.groupdict()["object"]
        replacement += match.groupdict()["end"]
        return replacement
    return function_str
