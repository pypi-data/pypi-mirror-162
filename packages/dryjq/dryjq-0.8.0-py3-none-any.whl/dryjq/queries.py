# -*- coding: utf-8 -*-

"""

dryjq.queries

Query parser and data structure address objects

Copyright (C) 2022 Rainer Schwarzbach

This file is part of dryjq.

dryjq is free software: you can redistribute it and/or modify
it under the terms of the MIT License.

dryjq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the LICENSE file for more details.

"""


import collections
import logging

from typing import Any, Dict, Iterator, List, Optional, Tuple

import yaml

import dryjq

from dryjq import access


DEFAULT_SEPARATOR_CODEPOINT = ord(dryjq.DEFAULT_SEPARATOR)

# Token types

TYPE_START = "QUERY START"
TYPE_END = "QUERY END"
TYPE_LITERAL = "LITERAL"
TYPE_SEPARATOR = "SEPARATOR"
TYPE_SUBSCRIPT_OPEN = "SUBSCRIPT OPENING"
TYPE_SUBSCRIPT_CLOSE = "SUBSCRIPT CLOSING"
TYPE_SPACING = "SPACING"
TYPE_ASSIGNMENT = "ASSIGNMENT"
TYPE_INTERNAL_JOINER = "INTERNAL JOINER"
TYPE_NONE = "NONE"

KNOWN_TOKENS = (
    TYPE_START,
    TYPE_END,
    TYPE_LITERAL,
    TYPE_SEPARATOR,
    TYPE_SUBSCRIPT_OPEN,
    TYPE_SUBSCRIPT_CLOSE,
    TYPE_SPACING,
    TYPE_ASSIGNMENT,
    TYPE_INTERNAL_JOINER,
    TYPE_NONE,
)


class Token:

    """Represents a single token"""

    def __init__(self, kind: str, content: Optional[Any] = None) -> None:
        """Store the token kind and content"""
        if kind not in KNOWN_TOKENS:
            raise ValueError(f"Unknown token kind {kind!r}")
        #
        self.__kind = kind
        self.__content = content

    @property
    def kind(self):
        """Return the kind"""
        return self.__kind

    @property
    def content(self):
        """return the content"""
        if self.__content is None:
            return f"<{self.kind}> token"
        #
        return self.__content


class Tokenizer:

    """Tokenize a query string for the parser"""

    quotes = (34, 39)  # Double and single quotes

    characters_lookup: Dict[str, Tuple[int, ...]] = {
        TYPE_ASSIGNMENT: (61,),  # Equals sign
        TYPE_SPACING: (9, 10, 13, 32),  # Tab, LF, CR, Space
        TYPE_SUBSCRIPT_OPEN: (91,),  # Opening square bracket
        TYPE_SUBSCRIPT_CLOSE: (93,),  # Closing square bracket
    }

    def __init__(
        self, separator_codepoint: int = DEFAULT_SEPARATOR_CODEPOINT
    ) -> None:
        """Initialize the tokenizer internal state"""
        self.__open_quote: Optional[int] = None
        self.__in_subscript = False
        self.__current_literal: List[int] = []
        self.__last_tk: Token = Token(TYPE_NONE)
        # Build token lookup map
        self.__lookup = {}
        for (tk_kind, characters) in self.characters_lookup.items():
            for single_character in characters:
                self.__lookup[single_character] = tk_kind
            #
        #
        if separator_codepoint in self.__lookup:
            raise ValueError(
                f"Separator codepoint {separator_codepoint} not allowed,"
                f" must not be any of {sorted(self.__lookup)}!"
            )
        #
        self.__lookup[separator_codepoint] = TYPE_SEPARATOR

    def add_token(self, kind: str, content: Optional[str] = None) -> Token:
        """Create a token, set self.__last_tk to it
        and return it
        """
        self.__last_tk = Token(kind, content=content)
        return self.__last_tk

    def add_current_literal(self) -> Token:
        """Return a new token from the current literal
        if it exists, else an INTERNAL_JOINER token
        """
        if not self.__current_literal:
            return Token(TYPE_INTERNAL_JOINER)
        #
        literal_data = "".join(
            chr(charcode) for charcode in self.__current_literal
        )
        logging.debug("Literal data: %r", literal_data)
        new_token = self.add_token(
            TYPE_LITERAL,
            content=literal_data,
        )
        self.__current_literal.clear()
        return new_token

    def reset(self) -> None:
        """Reset the tokenizer"""
        self.__open_quote = None
        self.__in_subscript = False
        self.__current_literal.clear()
        self.__last_tk = Token(TYPE_NONE)

    def process_character(self, charcode: int) -> Iterator[Token]:
        """Yield a single token or more,
        according to current character state
        """
        tk_kind = self.__lookup.get(charcode, TYPE_LITERAL)
        if self.__open_quote:
            self.__current_literal.append(charcode)
            if charcode == self.__open_quote:
                yield self.add_current_literal()
                self.__open_quote = None
            #
        elif self.__in_subscript:
            if tk_kind in TYPE_SPACING:
                yield self.add_token(tk_kind, chr(charcode))
                return
            #
            if tk_kind == TYPE_SUBSCRIPT_CLOSE:
                yield self.add_current_literal()
                yield self.add_token(tk_kind, chr(charcode))
                self.__in_subscript = False
                return
            #
            if tk_kind == TYPE_SUBSCRIPT_OPEN:
                logging.warning(
                    "Possible error: found unexpected %s character %r"
                    " in subscript",
                    tk_kind,
                    chr(charcode),
                )
                self.__current_literal.append(charcode)
            #
        elif tk_kind == TYPE_SUBSCRIPT_OPEN:
            yield self.add_current_literal()
            yield self.add_token(tk_kind, chr(charcode))
            self.__in_subscript = True
            return
        #
        if tk_kind in (TYPE_ASSIGNMENT, TYPE_SEPARATOR, TYPE_SPACING):
            yield self.add_current_literal()
            yield self.add_token(tk_kind, chr(charcode))
        elif charcode in self.quotes:
            if not self.__current_literal:
                self.__open_quote = charcode
            #
            self.__current_literal.append(charcode)
        else:
            self.__current_literal.append(charcode)
        #

    def tokenize(self, original_query: str) -> Iterator[Token]:
        """Yield tokens from a given query string"""
        self.reset()
        query_characters = collections.deque(original_query)
        yield self.add_token(TYPE_START)
        while query_characters:
            for current_token in self.process_character(
                ord(query_characters.popleft())
            ):
                if current_token.kind != TYPE_INTERNAL_JOINER:
                    logging.debug(
                        "%-20s -> %r",
                        current_token.kind,
                        current_token.content,
                    )
                    yield current_token
                #
            #
            if self.__last_tk.kind == TYPE_ASSIGNMENT:
                break
            #
        #
        last_literal_token = self.add_current_literal()
        if last_literal_token.kind != TYPE_INTERNAL_JOINER:
            yield last_literal_token
        #
        if self.__last_tk.kind == TYPE_ASSIGNMENT:
            # Append the remainder als a single literal
            yield Token(TYPE_LITERAL, content="".join(query_characters))
        #
        if self.__open_quote:
            raise ValueError(f"Unclosed quote ({self.__open_quote})!")
        #
        if self.__in_subscript:
            raise ValueError("Unclosed subscript ([)!")
        #
        yield Token(TYPE_END)


class Parser:

    """New Query parser"""

    append_component_before: Tuple[str, ...] = (
        TYPE_ASSIGNMENT,
        TYPE_END,
        TYPE_SEPARATOR,
        TYPE_SUBSCRIPT_CLOSE,
        TYPE_SUBSCRIPT_OPEN,
    )

    def __init__(self) -> None:
        """Initialize the tokenizer internal state"""
        self.__started = False
        self.__in_subscript = False
        self.__cache_remaining = False
        self.__collected_literals: List[str] = []
        self.__collected_components: List[access.PathComponent] = []

    def reset(self) -> None:
        """Reset the parser"""
        self.__started = False
        self.__in_subscript = False
        self.__cache_remaining = False
        self.__collected_literals.clear()
        self.__collected_components.clear()

    def __append_path_component(self, must_exist: bool = False) -> None:
        """Add a path component from the collected literals"""
        if not self.__collected_literals:
            if must_exist:
                raise ValueError("Empty path component")
            #
            return
        #
        # Join adjacent literals, but yaml load them
        # separately to enable mixing different quotes.
        # Allow other literals than strings.(only)
        # if exactly one literal was collected.
        if len(self.__collected_literals) > 1:
            component_index = "".join(
                yaml.safe_load(item) for item in self.__collected_literals
            )
        else:
            component_index = yaml.safe_load(self.__collected_literals[0])
        #
        self.__collected_components.append(
            access.PathComponent(
                component_index, in_subscript=self.__in_subscript
            )
        )
        self.__collected_literals.clear()

    def __consume_item_continue(self, item: Token) -> bool:
        """Consume one item and return False
        if this was the final iteration
        (i.e. an END item was encountered).
        """
        if not self.__started:
            # Allow spacing before the initial separator
            if item.kind in (TYPE_START, TYPE_SPACING):
                return True
            #
            if item.kind == TYPE_SEPARATOR:
                self.__started = True
                return True
            #
            raise ValueError(
                f"The query must start with a {TYPE_SEPARATOR} item!"
            )
        #
        if item.kind == TYPE_LITERAL:
            self.__collected_literals.append(item.content)
        elif item.kind in self.append_component_before:
            self.__append_path_component()
            if item.kind == TYPE_SUBSCRIPT_OPEN:
                self.__in_subscript = True
            elif item.kind == TYPE_SUBSCRIPT_CLOSE:
                self.__in_subscript = False
            elif item.kind == TYPE_ASSIGNMENT:
                self.__cache_remaining = True
            elif item.kind == TYPE_END:
                return False
            #
        #
        return True

    def parse_query(
        self,
        original_query: str,
        separator_codepoint: int = DEFAULT_SEPARATOR_CODEPOINT,
    ) -> Tuple[access.Path, Optional[str]]:
        """Parse the given query and return a tuple
        containing a data structure address
        and - optionally - a new value
        """
        self.reset()
        replacement = None
        cached_items: List[Token] = []
        tokenizer = Tokenizer(separator_codepoint=separator_codepoint)
        logging.debug("Found items in query:")
        for item in tokenizer.tokenize(original_query):
            logging.debug("%-20s -> %r", item.kind, item.content)
            if self.__cache_remaining:
                cached_items.append(item)
                continue
            #
            if not self.__consume_item_continue(item):
                break
            #
        #
        logging.debug(cached_items)
        if cached_items:
            last_item = cached_items[0]
            if last_item.kind == TYPE_END:
                logging.warning("Assuming empty assignment value")
                replacement = ""
            elif last_item.kind == TYPE_LITERAL:
                replacement = last_item.content
                if cached_items[1].kind != TYPE_END:
                    raise ValueError("Unexpected item")
                #
            else:
                raise ValueError(
                    f"Unexpected {last_item.kind} item"
                    f" {last_item.content!r}!"
                )
            #
        #
        logging.debug("Path components: %r", self.__collected_components)
        return (
            access.Path(*self.__collected_components),
            replacement,
        )


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
