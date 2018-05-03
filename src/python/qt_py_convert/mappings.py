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

import Qt

from qt_py_convert.log import get_logger
from qt_py_convert.general import _custom_misplaced_members

MAPPINGS_LOG = get_logger("mappings")


def misplaced_members(aliases, mappings):
    """
    misplaced_members uses the internal "_misplaced_members" from Qt.py as
    well as any "_custom_misplaced_members" that you have set to update the
    detected binding members. The Qt.py misplaced members aid in updating
    bindings to Qt5 compatible locations.

    :param aliases: Aliases is the replacement information that is build
        automatically from qt_py_convert.
    :type aliases: dict
    :param mappings: Mappings is information about the bindings that are used.
    :type mappings: dict
    :return: A tuple of aliases and mappings that have been updated.
    :rtype: tuple[dict,dict]
    """
    members = Qt._misplaced_members.get(Qt.__binding__.lower(), {})
    for binding in aliases["bindings"]:
        if binding in Qt._misplaced_members:
            MAPPINGS_LOG.debug("Merging {misplaced} to bindings".format(
                misplaced=Qt._misplaced_members.get(binding, {})
            ))
            members.update(Qt._misplaced_members.get(binding, {}))
        elif binding in _custom_misplaced_members:
            members.update(_custom_misplaced_members.get(binding, {}))
        else:
            MAPPINGS_LOG.debug(
                "Could not find misplaced members for {}".format(binding)
            )

        _msg = "Replacing \"{original}\" with \"{replacement}\" in mappings"
        if members:
            for source in members:
                replaced = False
                dest = members[source]
                if isinstance(dest, (list, tuple)):
                    dest, _ = members[source]
                for current_key in mappings:
                    if mappings[current_key] == source:
                        MAPPINGS_LOG.debug(
                            _msg.format(
                                original=mappings[current_key],
                                replacement=dest
                            )
                        )
                        mappings[current_key] = dest
                        replaced = True
                if not replaced:
                    MAPPINGS_LOG.debug(
                        "Adding {bind} in mappings".format(bind=dest)
                    )
                    mappings[source] = dest
    return aliases, mappings


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
