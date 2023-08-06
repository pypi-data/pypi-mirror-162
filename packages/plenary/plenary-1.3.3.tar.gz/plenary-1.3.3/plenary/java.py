# -*- coding: utf-8 -*-
import re
import typing

# Regex for finding assignments, i.e. <object name>.<variable name> = <value>;
_RE_JS_ASSIGNMENT = re.compile(r'^([\w.]+)([\w\d\[\]]*)\s+=\s+([^;]+);$')


def javascript_parse(js_code: str) -> typing.Mapping[str, typing.Any]:
    """ Extract assignments from Java/JavaScript code, specifically looking for object properties.

    This likely doesn't work well with proper JSON, but there's an existing module to handle that. This is a standalone
    and fairly trivial implementation of a parser, so it would normally get many things wrong in real-world
    applications, but for IoT-style minimal applications it's fine.

    It was developed to extract data from JavaScript code passed to the (very outdated) web front-end of an MKS
    mass flow controller (MFC).

    :param js_code: Java/JavaScript code as a string
    :return: dictionary of Java/JavaScript objects with assigned properties
    """
    js_namespace = {}

    for js_line in js_code.split('\n'):
        # Fetch only lines that look like assignments
        js_assignment = _RE_JS_ASSIGNMENT.match(js_line)

        # Ignore non-assignment lines or lines creating empty objects
        if js_assignment is None or js_assignment[3].startswith('new '):
            continue

        js_obj_name = js_assignment[1].split('.')
        js_index = int(js_assignment[2][1:-1]) if len(js_assignment[2]) > 0 else None
        js_value = eval(js_assignment[3])

        # Allocate space for name
        js_namespace_node = js_namespace

        for name in js_obj_name[:-1]:
            if name not in js_namespace_node:
                js_namespace_node[name] = {}

            js_namespace_node = js_namespace_node[name]

        # Allocate space for value
        if js_index is None:
            js_namespace_node[js_obj_name[-1]] = js_value
        else:
            if js_obj_name[-1] not in js_namespace_node:
                js_namespace_node[js_obj_name[-1]] = []

            js_namespace_node[js_obj_name[-1]].append(js_value)

    return js_namespace
