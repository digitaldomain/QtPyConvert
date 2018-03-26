import re

from qt_py_convert.external import Qt


def convert_mappings(aliases, mappings):
    """
    convert_mappings will build a proper mapping dictionary using any
    aliases that we have discovered previously.
    It builds regular expressions based off of the Qt._common_members and will
    replace the mappings that are used with updated ones in Qt.py

    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param mappings: Mappings is information about the bindings that are used.
    :type mappings: dict
    :return: _convert_mappings will just return the mappings dict,
        however it is updating the aliases["used"] set.
    :rtype: dict
    """
    expressions = [
        re.compile(
            r"(?P<module>{modules})\.(?P<widget>{widgets})$".format(
                # Regular expression
                modules="|".join(
                    re.escape(name) for name in Qt._common_members.keys()
                ),
                widgets="|".join(
                    re.escape(widget) for widget in Qt._common_members[module]
                )
            )
        )
        for module in Qt._common_members.keys()
    ]
    for from_mapping in mappings:
        iterable = zip(Qt._common_members.keys(), expressions)
        for module_name, expression in iterable:
            modified_mapping = expression.sub(
                r"{module}.\2".format(module=module_name),
                mappings[from_mapping]
            )
            if modified_mapping != mappings[from_mapping]:
                # Mapping changed
                # _---------------------------_ #
                # We shouldn't be adding it here.
                # We don't know if it's used yet.
                #       aliases["used"].add(module_name)
                mappings[from_mapping] = modified_mapping
    return mappings
