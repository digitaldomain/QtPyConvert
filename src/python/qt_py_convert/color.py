import os
import subprocess
import sys


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
    has_colors = p.communicate()[0].strip("\n")
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

