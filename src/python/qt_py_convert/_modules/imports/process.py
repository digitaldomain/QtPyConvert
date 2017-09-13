from qt_py_convert.general import __supported_bindings__, _color, AliasDict


class Processes(object):
    @staticmethod
    def _build_child_name(child):
        return ".".join([child_part.dumps() for child_part in child.value])

    @staticmethod
    def _no_second_level_module(node, _child_parts):

        print(
            "Changing {old} to {new} at line {line}".format(
                old=str(node).strip("\n"),
                new=_color(35, "import Qt"),
                line=node.absolute_bounding_box.top_left.line-1
            )
        )
        node.replace("import Qt")

    @classmethod
    def _process_import(cls, red, objects):
        binding_aliases = AliasDict
        mappings = {}

        # Replace each node
        for node, binding in objects:
            for child in node.value:
                _child_name = cls._build_child_name(child)
                _child_as_name = child.target

                _child_parts = _child_name.replace(binding, "")
                _child_parts = _child_parts.lstrip(".").split(".")

                # Check to see if there is a second level module
                if len(_child_parts) and _child_parts[0]:
                    second_level_module = _child_parts[0]
                else:
                    cls._no_second_level_module(node, _child_parts)
                    if _child_as_name:
                        mappings[_child_as_name] = "Qt"
                    continue

                mappings[_child_as_name or _child_name] = ".".join(_child_parts)
                print(
                    "Changing {old} to {new} at line {line}".format(
                        old=str(node.parent).strip("\n"),
                        new=_color(
                            35,
                            "from Qt import {key}".format(
                                key=second_level_module
                            )
                        ),
                        line=node.parent.absolute_bounding_box.top_left.line - 1
                    )
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
    def filter_function(value):
        """
        filter_function takes an AtomTrailersNode or a DottedNameNode and will filter them out if they match something that
        has changed in psep0101
        """
        _raw_module = value.dumps()
        # See if that import is in our __supported_bindings__
        for supported_binding in __supported_bindings__:
            if _raw_module.startswith(supported_binding):
                store[Processes.IMPORT_STR].add(
                    (value, supported_binding)
                )
                return True
    return filter_function


def process(red, **kwargs):

    issues = {
        Processes.IMPORT_STR: set(),
    }
    red.find_all("ImportNode", value=import_process(issues))
    key = Processes.IMPORT_STR

    if issues[key]:
        return getattr(Processes, key)(red, issues[key])
    else:
        return AliasDict, {}
