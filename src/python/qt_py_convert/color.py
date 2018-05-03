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
import subprocess
import sys
from builtins import bytes

class ANSI(object):
    """ANSI is a namespace object. Useful for passing values into "_color" """
    class colors(object):
        white = 29
        black = 30
        red = 31
        green = 32
        orange = 33
        blue = 34
        purple = 35
        teal = 36
        gray = 37

    class styles(object):
        plain = 0
        strong = 1
        underline = 4
        reversed = 7
        strike = 9


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    p = subprocess.Popen(
        ["tput", "colors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    has_colors = p.communicate()[0].strip(bytes("\n", encoding="UTF-8"))
    try:
        has_colors = int(has_colors)
    except:
        has_colors = False

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if (not supported_platform or not is_a_tty) and not has_colors:
        return False
    return True


SUPPORTS_COLOR = supports_color()


def color_text(color=ANSI.colors.white, text="", style=ANSI.styles.plain):
    """
    _color will print the ansi text coloring code for the text.

    :param color: Ansi color code number.
    :type color: int
    :param text: Text that you want colored.
    :type text: str
    :return: The colored version of the text
    :rtype: str
    """
    if not SUPPORTS_COLOR:
        return text
    return "\033[{color};{style}m{message}\033[0m".format(
        style=style, color=color, message=text
    )

