# -*- coding: utf-8 -*-

"""

dryjq.cli_commons

Command line common functionality

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

from typing import Dict, IO, List, Optional, Type

import yaml

import dryjq

from dryjq import access
from dryjq import streams


#
# Constants
#


RETURNCODE_OK = 0
RETURNCODE_ERROR = 1


#
# classes
#


class Program:

    """Command line program"""

    name: str = "dryjq"
    description: str = "Drastically Reduced YAML / JSON Query"
    query_option: bool = True
    modify_in_place_option: bool = True
    default_output_format: str = dryjq.FORMAT_INPUT

    allowed_formats: Dict[str, str] = {
        dryjq.FORMAT_JSON: "set output format to JSON",
        dryjq.FORMAT_YAML: "set output fromat to YAML",
        dryjq.FORMAT_INPUT: "keep input format",
        dryjq.FORMAT_TOGGLE: "change JSON to YAML or vice versa",
    }

    def __init__(self, args):
        """Parse command line arguments"""
        self.arguments = self.__parse_args_init_logger(args)

    @classmethod
    def complete_format(cls, input_format: str) -> str:
        """Lookup the matching format"""
        lower_input_format = input_format.lower()
        for candidate in cls.allowed_formats:
            if candidate.lower().startswith(lower_input_format):
                return candidate
            #
        #
        raise ValueError(f"Unsupported format {input_format!r}!")

    def __parse_args_init_logger(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments, initialize logging
        and return the arguments namespace.
        """
        main_parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
        )
        main_parser.set_defaults(
            loglevel=logging.WARNING,
            query=dryjq.DEFAULT_SEPARATOR,
            output_format=self.default_output_format,
            indent=dryjq.DEFAULT_INDENT,
            inplace=False,
        )
        main_parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {dryjq.__version__}",
            help="print version and exit",
        )
        if self.modify_in_place_option:
            main_parser.add_argument(
                "-i",
                "--inplace",
                action="store_true",
                help="modify the input file in place instead of writing"
                " the result to standard output",
            )
        #
        logging_group = main_parser.add_argument_group(
            "Logging options", "control log level (default is WARNING)"
        )
        verbosity = logging_group.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-d",
            "--debug",
            action="store_const",
            const=logging.DEBUG,
            dest="loglevel",
            help="output all messages (log level DEBUG)",
        )
        verbosity.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const=logging.INFO,
            dest="loglevel",
            help="be more verbose (log level INFO)",
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=logging.ERROR,
            dest="loglevel",
            help="be more quiet (log level ERROR)",
        )
        output_group = main_parser.add_argument_group(
            "Output options", "control output formatting"
        )
        format_choices = ", ".join(
            f"{key!r}: {value}"
            for (key, value) in self.allowed_formats.items()
        )
        output_group.add_argument(
            "-o",
            "--output-format",
            type=self.complete_format,
            help=f"output format (choice of {format_choices};"
            " default: %(default)r)",
        )
        output_group.add_argument(
            "--indent",
            choices=(2, 4, 8),
            type=int,
            help="indentation depth of blocks, in spaces"
            " (default: %(default)s)",
        )
        output_group.add_argument(
            "--sort-keys",
            action="store_true",
            help="sort mapping keys"
            " (by default, mapping keys are left in input order)",
        )
        if self.query_option:
            main_parser.add_argument(
                "query",
                nargs="?",
                help="the query (simplest form of yq/jq syntax,"
                " default is %(default)r).",
            )
        #
        main_parser.add_argument(
            "input_file",
            nargs="?",
            help="the input file name"
            " (by default, data will be read from standard input)",
        )
        arguments = main_parser.parse_args(args)
        logging.basicConfig(
            format="%(levelname)-8s | (%(funcName)s:%(lineno)s) %(message)s",
            level=arguments.loglevel,
        )
        return arguments

    def write_filtered_data(
        self,
        handler_class: Type[streams.StreamHandler],
        stream: IO,
        data_path: access.Path,
        replacement_value: Optional[str] = None,
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
            file_handler.dump_data(
                output_format=self.arguments.output_format,
                indent=self.arguments.indent,
                sort_keys=self.arguments.sort_keys,
            )
            file_handler.write_output()
        except (TypeError, ValueError, yaml.YAMLError) as error:
            for line in str(error).splitlines():
                logging.error(line)
            #
            return RETURNCODE_ERROR
        #
        return RETURNCODE_OK

    def execute(
        self,
        data_path: access.Path,
        replacement_value: Optional[str] = None,
    ) -> int:
        """Execute the program"""
        display_mode = "extract mode"
        replace_mode = replacement_value is not None
        if replace_mode:
            display_mode = "replace mode"
        elif not data_path:
            display_mode = f"{display_mode} (passthrough)"
        #
        logging.info("Operating in %s.", display_mode)
        if self.arguments.input_file is None:
            if self.arguments.inplace:
                logging.warning("Cannot modify <stdin> in place")
            #
            logging.info("- ↓↓↓ Reading data from standard input")
            return self.write_filtered_data(
                streams.StreamHandler,
                sys.stdin,
                data_path,
                replacement_value=replacement_value,
            )
        #
        file_helper = streams.FileHelper(
            self.arguments.input_file,
            modify_in_place=self.arguments.inplace,
            replace_mode=replace_mode,
        )
        with file_helper.open(encoding="utf-8") as input_file:
            file_helper.lock(input_file)
            logging.info(
                "----- Reading data from file: %s", file_helper.file_name
            )
            returncode = self.write_filtered_data(
                file_helper.handler_class,
                input_file,
                data_path,
                replacement_value=replacement_value,
            )
            file_helper.unlock(input_file)
        #
        return returncode


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
