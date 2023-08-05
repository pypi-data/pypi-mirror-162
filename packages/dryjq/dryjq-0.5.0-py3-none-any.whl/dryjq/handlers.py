# -*- coding: utf-8 -*-

"""

dryjq.handlers

Data structure, stream and file handlers

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import json
import logging
import sys

from typing import Any, IO, Optional

import yaml

import dryjq

from dryjq import queries


class DataHandler:

    """Data structure handler"""

    def __init__(self, data: Any) -> None:
        """Initialize the handler with data"""
        self.filtered_data = data
        self.updated_data = False

    def dump_data(
        self,
        output_format: str = dryjq.FORMAT_YAML,
        indent: int = dryjq.DEFAULT_INDENT,
        sort_keys: bool = False,
    ) -> str:
        """Return a dump of self.data"""
        if output_format == dryjq.FORMAT_JSON:
            return json.dumps(
                self.filtered_data,
                indent=indent,
                ensure_ascii=True,
                sort_keys=sort_keys,
            )
        #
        output = yaml.safe_dump(
            self.filtered_data,
            allow_unicode=True,
            default_flow_style=False,
            indent=indent,
            sort_keys=sort_keys,
            explicit_end=False,
        )
        if isinstance(self.filtered_data, (dict, list)):
            return output
        #
        if output.rstrip().endswith("\n..."):
            output = output.rstrip()[:-3]
        #
        return output

    def execute_single_query(
        self,
        data_path: queries.DataStructureAddress,
        replacement_value: Optional[str] = None,
    ) -> None:
        """Execute the provided query, modifying self.data"""
        logging.debug("Filtered data before executing the query:")
        logging.debug("%r", self.filtered_data)
        if replacement_value is None:
            self.filtered_data = data_path.get_value(self.filtered_data)
        else:
            self.filtered_data = data_path.replace_value(
                self.filtered_data, yaml.safe_load(replacement_value.strip())
            )
            self.updated_data = True
        #
        logging.debug("Filtered data after executing the query:")
        logging.debug("%r", self.filtered_data)


class StreamHandler:

    """YAML or JSON file reader"""

    def __init__(self, stream_io: IO) -> None:
        """Read all data from the stream"""
        contents = stream_io.read()
        try:
            self.data_handler = DataHandler(json.loads(contents))
        except json.JSONDecodeError:
            self.data_handler = DataHandler(yaml.safe_load(contents))
            self.__input_format = dryjq.FORMAT_YAML
        else:
            self.__input_format = dryjq.FORMAT_JSON
        #
        self.__original_contents = contents
        self.__stream_io = stream_io

    @property
    def stream_io(self) -> IO:
        """Return the stream handle"""
        return self.__stream_io

    @property
    def original_contents(self) -> str:
        """Return the original contents"""
        return self.__original_contents

    def get_data_dump(self, **output_options: Any) -> str:
        """Get a dump of currently filtered data
        from the data handler
        """
        if not output_options.get("output_format"):
            output_options["output_format"] = self.__input_format
        #
        return self.data_handler.dump_data(**output_options)

    def write_output(self, **output_options: Any) -> None:
        """Write output to stdout"""
        data_dump = self.get_data_dump(**output_options).rstrip()
        sys.stdout.write(f"{data_dump}\n")


class FileReader(StreamHandler):

    """File reader"""

    def __init__(self, stream_io: IO) -> None:
        """Go to the first byte in the file,
        then act as a normal StreamReader instance
        """
        stream_io.seek(0)
        super().__init__(stream_io)


class FileWriter(FileReader):

    """File writer
    No locking done here, the caller is responsible for that.
    """

    def write_output(self, **output_options: Any) -> None:
        """Write output to the file if data has changed"""
        data_dump = self.get_data_dump(**output_options)
        if data_dump == self.original_contents:
            logging.warning("File contents did not change.")
            return
        #
        self.stream_io.seek(0)
        self.stream_io.truncate(0)
        self.stream_io.write(data_dump)


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
