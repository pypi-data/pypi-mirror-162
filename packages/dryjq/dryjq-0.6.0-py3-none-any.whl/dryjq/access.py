# -*- coding: utf-8 -*-

"""

dryjq.access

Data structure access using Path objects

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import copy
import logging

from typing import Any


class PathComponent:

    """single index component of a Path"""

    def __init__(self, index: Any, in_subscript: bool = False) -> None:
        """Initialize with the index"""
        self.__index = index
        self.__allow_lists = in_subscript
        if not in_subscript:
            self.__reason = "not in subscript"
        if not isinstance(index, int):
            self.__allow_lists = False
            self.__reason = "not a valid list index"
        #

    def get_value(self, data_structure: Any) -> Any:
        """Get the value from data_structure[self.__index]"""
        if not isinstance(data_structure, (list, dict)):
            raise TypeError(
                f"Index {self.__index!r} is not suitable for scalar value"
                f" {data_structure!r}!"
            )
        #
        if isinstance(data_structure, list) and not self.__allow_lists:
            raise TypeError(
                f"Index {self.__index!r} is not suitable for lists"
                f" ({self.__reason})!"
            )
        #
        try:
            value = data_structure[self.__index]
        except (IndexError, KeyError) as error:
            raise ValueError(
                f"Index {self.__index!r} not found in {data_structure!r}!"
            ) from error
        #
        logging.debug("Value at %r is %r", self.__index, value)
        return value

    def replace_value(self, data_structure: Any, new_value: Any) -> None:
        """Modify data_structure in place:
        replace the value at the existing index by new_value
        """
        # Ensure the index aready exists
        self.get_value(data_structure)
        data_structure[self.__index] = new_value

    def __repr__(self) -> str:
        """Return a representation"""
        if self.__allow_lists:
            purpose = "for maps and lists"
        else:
            purpose = "for maps only"
        #
        return f"<Index {self.__index!r} ({purpose})>"


class Path:

    """Address in data structures,
    a sequence of PathComponent instances.
    """

    def __init__(self, *components: PathComponent) -> None:
        """Initialize the internal components"""
        self.__complete_path = components

    def get_value(self, data_structure: Any) -> Any:
        """Get a value or substructure from data_structure
        using self.__complete_path
        """
        current_value = data_structure
        for element in self.__complete_path:
            current_value = element.get_value(current_value)
        #
        return current_value

    def replace_value(self, data_structure: Any, new_value: Any) -> Any:
        """Replace a value in the data structure,
        and return a copy with the replaced value
        """
        if not self.__complete_path:
            return new_value
        #
        ds_copy = copy.deepcopy(data_structure)
        current_value = ds_copy
        for element in self.__complete_path[:-1]:
            current_value = element.get_value(current_value)
        #
        last_element = self.__complete_path[-1]
        last_element.replace_value(current_value, new_value)
        return ds_copy


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
