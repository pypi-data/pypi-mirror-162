#!/usr/bin/env python3

# Standard libraries
from os.path import expandvars
from re import sub as regex_sub

# Environment class, pylint: disable=too-few-public-methods
class Environment:

    # Expand
    @staticmethod
    def expand(value, unknowns=False):

        # Variables
        last = None
        result = value

        # Expand while needed
        while last != result:
            last = result
            result = expandvars(result)

        # Expand unknown variables
        if unknowns:
            result = regex_sub(r'(?<!\\)\${?[A-Za-z_][A-Za-z0-9_]*}?', '', result)

        # Result
        return result
