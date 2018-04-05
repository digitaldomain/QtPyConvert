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
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

def pythonize_arg(arg):
    if arg in dir(builtins):
        return arg
    elif "[" in arg or "list" in arg.lower():
        return "list"
    elif arg == "QString":
        return "str"
    elif arg == "QVariant":
        return "object"
    elif arg.startswith("Q"):
        return arg
    else:
        return "object"


def parse_args(arg_str):
    args = arg_str.split(",")
    _final = []
    for arg in args:
        if not arg:
            continue
        arg_c = arg.strip("&").strip().split(" ")[-1]

        arg_c = pythonize_arg(arg_c)

        _final.append(arg_c)
    final_args = ", ".join(_final)
    return final_args
