from qt_py_convert.general import _color, AliasDict


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
        _temp = __import__(binding, globals(), locals(), levels)
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
                31,
                "Replacing star import \"%s\" with explicit import \"%s\"" % (
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
    def filter_function(value):
        for target in value.parent.targets:
            if target.type == "star":
                store[Processes.EXPAND_STR].add(value)
                return True

    return filter_function


def process(red, **kwargs):
    issues = {
        Processes.EXPAND_STR: set(),
    }
    print(_color(
        31, "WARNING: \"import star\" used. We are bootstrapping code!"
    ))
    print(_color(
        31, "This will be very slow. It's your own fault."
    ))
    values = red.find_all("FromImportNode", value=star_process(issues))

    mappings = getattr(Processes, Processes.EXPAND_STR)(
        red, issues[Processes.EXPAND_STR]
    )
    return AliasDict, mappings
