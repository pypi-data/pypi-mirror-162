# -*- coding: utf-8 -*-
from random import choice
from string import hexdigits

__all__ = [
    'hex_str'
]


def hex_str(length: int = 8) -> str:
    """ Generate a random hexadecimal string of a specified length in lower case.

    :param length: desired string length
    :return: random hexadecimal string of desired length in lower case
    """
    return ''.join(choice(hexdigits[:16]) for _ in range(length))
