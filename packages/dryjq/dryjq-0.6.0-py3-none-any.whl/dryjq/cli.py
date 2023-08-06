# -*- coding: utf-8 -*-

"""

dryjq.cli

Command line interface

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import argparse
import logging

import sys

from typing import Any, IO, List, Optional, Type

import yaml

import dryjq

from dryjq import access
from dryjq import queries
from dryjq import streams


#
# Constants
#


RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# Functions
#


def execute_query(
    handler_class: Type[streams.StreamHandler],
    stream: IO,
    data_path: access.Path,
    replacement_value: Optional[str] = None,
    **output_options: Any,
) -> int:
    """Execute the query, write output and return the returncode"""
    try:
        file_handler = handler_class(stream)
    except (yaml.YAMLError, yaml.composer.ComposerError) as error:
        for line in str(error).splitlines():
            logging.error(line)
        #
        return RETURNCODE_ERROR
    #
    try:
        file_handler.execute_single_query(
            data_path, replacement_value=replacement_value
        )
        file_handler.write_output(**output_options)
    except (TypeError, ValueError, yaml.YAMLError) as error:
        for line in str(error).splitlines():
            logging.error(line)
        #
        return RETURNCODE_ERROR
    #
    return RETURNCODE_OK


def main(args: Optional[List[str]] = None) -> int:
    """Parse command line arguments and execute the matching function"""
    main_parser = argparse.ArgumentParser(
        prog="dryjq",
        description="Drastically Reduced YAML / JSON Query",
    )
    main_parser.set_defaults(
        loglevel=logging.INFO, query=".", output_indent=dryjq.DEFAULT_INDENT
    )
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="loglevel",
        help="Output all messages including debug level",
    )
    main_parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.ERROR,
        dest="loglevel",
        help="Limit message output to errors",
    )
    main_parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit",
    )
    main_parser.add_argument(
        "--modify-in-place",
        action="store_true",
        help="Modify the input file in place instead of writing"
        " the result to standard output.",
    )
    output_group = main_parser.add_argument_group(
        "Output options", "control how output will be formatted"
    )
    output_group.add_argument(
        "-of",
        "--output-format",
        type=str.upper,
        choices=dryjq.SUPPORTED_FORMATS,
        help="File format. By default, the detected input format is used.",
    )
    output_group.add_argument(
        "-oi",
        "--output-indent",
        choices=(2, 4, 8),
        type=int,
        help="Indentation depth of blocks, in spaces (default: %(default)s).",
    )
    output_group.add_argument(
        "-osk",
        "--output-sort-keys",
        action="store_true",
        help="Sort mapping keys."
        " By default, mapping keys are left in input order.",
    )
    main_parser.add_argument(
        "query",
        nargs="?",
        help="The query (simplest form of yq/jq syntax,"
        " default is %(default)r).",
    )
    main_parser.add_argument(
        "input_file",
        nargs="?",
        help="The input file name."
        " By default, data will be read from standard input.",
    )
    arguments = main_parser.parse_args(args)
    if arguments.version:
        print(dryjq.__version__)
        return RETURNCODE_OK
    #
    logging.basicConfig(
        format="%(levelname)-8s | (%(funcName)s:%(lineno)s) %(message)s",
        level=arguments.loglevel,
    )
    data_path, replacement_value = queries.Parser().parse_query(
        arguments.query
    )
    output_options = dict(
        output_format=arguments.output_format,
        indent=arguments.output_indent,
        sort_keys=arguments.output_sort_keys,
    )
    if arguments.input_file is None:
        if arguments.modify_in_place:
            logging.warning("Cannot modify <stdin> in place")
        #
        return execute_query(
            streams.StreamHandler,
            sys.stdin,
            data_path,
            replacement_value=replacement_value,
            **output_options,
        )
    #
    file_helper = streams.FileHelper(
        arguments.input_file,
        modify_in_place=arguments.modify_in_place,
        replace_value_mode=(replacement_value is not None),
    )
    with file_helper.open(encoding="utf-8") as input_file:
        file_helper.lock(input_file)
        returncode = execute_query(
            file_helper.handler_class,
            input_file,
            data_path,
            replacement_value=replacement_value,
            **output_options,
        )
        file_helper.unlock(input_file)
    #
    return returncode


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
