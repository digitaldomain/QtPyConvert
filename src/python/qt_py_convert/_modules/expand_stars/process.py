"""
The imports module is designed to fix the import statements.
"""
from qt_py_convert.general import _color, AliasDict, ANSI


class Processes(object):
    @staticmethod
    def _get_children(binding, levels=None):
        """
        You have done the following:
        >>> from <binding>.<levels> import *

        And I hate you a little bit.
        I am changing it to the following:
        >>> from <binding> import <levels>

        But I don't know what the heck you used in the *
        So I am just getting everything bootstrapped in. Sorry-not-sorry
        """
        def _members(_mappings, _module_, module_name):
            members = filter(
                lambda m: True if not m.startswith("__") else False,
                dir(_module)
            )
            for member in members:
                mappings[member] = "{mod}.{member}".format(
                    mod=module_name,
                    member=member
                )

        mappings = {}
        if levels is None:
            levels = []
        try:
            _temp = __import__(binding, globals(), locals(), levels)
        except ImportError as err:
            strerr = str(err).replace("No module named", "")

            raise ImportError(
                "Attempting to manually replace a star import from \"{mod}\" "
                "failed. The following error ocurred while attempting:\n{err}"
                    .format(mod=strerr, err=str(err))
            )
        if not levels:
            _module = _temp
            _members(mappings, _module, module_name=binding)
        else:
            for level in levels:
                _module = getattr(_temp, level)
                _members(mappings, _module, module_name=level)
        return mappings

    @classmethod
    def _process_star(cls, red, stars):
        """
        _process_star is designed to replace from X import * methods.

        :param red: redbaron process. Unused in this method.
        :type red: redbardon.RedBaron
        :param stars: List of redbaron nodes that matched for this proc.
        :type stars: list
        """
        mappings = {}
        for star in stars:
            from_import = star.parent
            binding = from_import.value[0]
            second_level_modules = None
            if len(star.parent.value) > 1:
                second_level_modules = [star.parent.value[1].dumps()]
            if len(star.parent.value) > 2:
                pass

            children = cls._get_children(binding.dumps(), second_level_modules)
            if second_level_modules is None:
                second_level_modules = children
            text = "from {binding} import {slm}".format(
                binding="Qt",
                slm=", ".join([name for name in second_level_modules])
            )
            print(_color(
                color=ANSI.colors.red,
                text="Replacing star import \"%s\" with explicit \"%s\"" % (
                    star.dumps(), text
                )
            ))
            mappings.update(children)
            # star.replace(
            #     text
            # )
        return mappings

    EXPAND_STR = "EXPAND"
    EXPAND = _process_star


def star_process(store):
    """
    star_process is one of the more complex handlers for the _modules.

    :param store: Store is the issues dict defined in "process"
    :type store: dict
    :return: The filter_function callable.
    :rtype: callable
    """
    def filter_function(value):
        for target in value.parent.targets:
            if target.type == "star":
                store[Processes.EXPAND_STR].add(value)
                return True

    return filter_function


def process(red, **kwargs):
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
        Processes.EXPAND_STR: set(),
    }
    print(_color(
        color=ANSI.colors.red,
        text="WARNING: \"import star\" used. We are bootstrapping code!"
    ))
    print(_color(
        color=ANSI.colors.red,
        text="This will be very slow. It's your own fault."
    ))
    values = red.find_all("FromImportNode", value=star_process(issues))

    mappings = getattr(Processes, Processes.EXPAND_STR)(
        red, issues[Processes.EXPAND_STR]
    )
    return AliasDict, mappings
