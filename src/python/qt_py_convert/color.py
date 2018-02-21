import difflib
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
    return "\033[{style};{color}m{message}\033[0m".format(
        style=style, color=color, message=text
    )


def highlight_diffs(start, finish, sep=(".", " ", ",", "(")):
    if not SUPPORTS_COLOR:
        return start, finish

    slist = start.split(sep[0])
    flist = finish.split(sep[0])
    seqm = difflib.SequenceMatcher(a=slist, b=flist)
    slist_out = []
    flist_out = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == "replace":
            slist_intermediate = []
            flist_intermediate = []
            for start_part, finish_part in zip(slist[a0:a1],
                                               flist[b0:b1]):
                spart_repl, fpart_repl = start_part, finish_part
                if len(sep) > 1:
                    spart_repl, fpart_repl = \
                        highlight_diffs(start_part, finish_part, sep=sep[1:])
                if spart_repl != start_part or fpart_repl != finish_part:
                    slist_intermediate.append(spart_repl)
                    flist_intermediate.append(fpart_repl)
                else:
                    slist_intermediate.append(start_part)
                    flist_intermediate.append(finish_part)

            for sitem, fitem in zip(slist_intermediate, flist_intermediate):
                if sitem != fitem:
                    slist_out.append(color_text(
                        color=ANSI.colors.green,
                        text=sitem,
                        style=ANSI.styles.strong
                    ))
                    flist_out.append(color_text(
                        color=ANSI.colors.green,
                        text=fitem,
                        style=ANSI.styles.strong
                    ))
                else:
                    slist_out.append(sitem)
                    flist_out.append(fitem)
        elif opcode == "equal":
            slist_out.extend(map(
                lambda x: color_text(color=ANSI.colors.gray, text=x),
                slist[a0:a1]
            ))
            flist_out.extend(map(
                lambda x: color_text(color=ANSI.colors.gray, text=x),
                flist[b0:b1]
            ))
        elif opcode == "delete":
            slist_out.extend(map(
                lambda x: color_text(
                    color=ANSI.colors.green,
                    text=x,
                    style=ANSI.styles.strike
                ),
                slist[a0:a1]
            ))
            flist_out.extend(map(
                lambda x: color_text(
                    color=ANSI.colors.green,
                    text=x,
                    style=ANSI.styles.strike),
                flist[b0:b1]
            ))
        else:
            slist_out += slist[a0:a1]
            flist_out += flist[b0:b1]
    return sep[0].join(slist_out), sep[0].join(flist_out)
