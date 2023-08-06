# -*- coding: utf-8 -*-

"""

dryjq.__main__

Module execution entry point

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import sys

from typing import List, Optional

import dryjq

from dryjq import access
from dryjq import cli_commons


#
# Classes
#


class ConvertProgram(cli_commons.Program):

    """Conversion program"""

    name: str = "dryjq.convert"
    description: str = "Drastically Reduced YAML / JSON Query: convert files"
    query_option: bool = False
    modify_in_place_option: bool = False
    default_output_format: str = dryjq.FORMAT_TOGGLE


#
# Functions
#


def main(args: Optional[List[str]] = None) -> int:
    """Parse command line arguments and execute the matching function"""
    program = ConvertProgram(args)
    return program.execute(access.Path())


if __name__ == "__main__":
    sys.exit(main())


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
