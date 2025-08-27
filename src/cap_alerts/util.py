"""Utility functions for cap_alerts."""

from datetime import datetime
from logging import Formatter, LogRecord

import pyparsing as pp
from lxml.etree import _Element

from cap_alerts import NS_MAP


class IPAWSAlertsError(Exception):
    """Base class for custom exceptions in this module."""


class MalformedError(IPAWSAlertsError):
    """Malformed polygon exception class."""

    def __init__(self, message: str, detail: str) -> None:
        """Malformed polygon exception.

        Args:
            message (str): message about error
            detail (str): details about error
        """
        super().__init__(message)
        self.detail = detail


def convint(st: str) -> int:
    """Forcefuly convert a number like string to integer.

        If it looks like a float, will convert via float.

    Args:
        st (str): string to convert

    Returns:
        int: integer found
    """
    try:
        return int(st)
    except ValueError:  # If you get a ValueError
        return int(float(st))


def format_time(self: Formatter, record: LogRecord, datefmt: str | None = None) -> str:  # noqa: ARG001
    """Time formatter for logging.

    Args:
        self (Formatter): formatter object
        record (LogRecord): the log reccord
        datefmt (str | None, optional): a specified dateformat. Defaults to None.

    Returns:
        str: formatted time
    """
    return (
        datetime.fromtimestamp(record.created)
        .astimezone()
        .isoformat(timespec="milliseconds")
    )


def find(elem: _Element, xpath: str) -> _Element | None:
    """Finds the first matching subelement, by tag name or path.

    Wrapper arround lxml function, applying namespace map.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        _Element | None: found element, if any.
    """
    return elem.find(xpath, namespaces=NS_MAP)


def findtext(elem: _Element, xpath: str) -> str | None:
    """Finds text for the first matching subelement, by tag name or path.

    Wrapper around lxml function, applying namespace map.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        str | None: found text
    """
    return elem.findtext(xpath, namespaces=NS_MAP)


def findall(elem: _Element, xpath: str) -> list[_Element]:
    """Finds all matching subelements, by tag name or path.

    Wrapper around lxml function, applying namespace map.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        list[_Element]: list of found subelements
    """
    return elem.findall(xpath, namespaces=NS_MAP)


def findint(elem: _Element, xpath: str) -> int | None:
    """Convenience wrapper arround findtext that returns an init.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        int | None: found integer
    """
    return convint(x) if (x := findtext(elem, xpath)) is not None else None


def findalltext(elem: _Element, xpath: str) -> list[str]:
    """A convenience hybrid of findall and findtext.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        list[str]: list of strings found
    """
    return [x.text for x in findall(elem, xpath) if x.text is not None]


quoted_str_parser = pp.OneOrMore(
    pp.QuotedString(quote_char='"') | pp.Word(pp.printables, exclude_chars='"'),
)


def extract_quoted(elem: _Element, xpath: str) -> list[str]:
    """Find element with xpath and extract a list of quoted, comma seperated tokens.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        list[str]: list of strings
    """
    text = findtext(elem, xpath)
    if text:
        results = quoted_str_parser.parse_string(text)
        return results.as_list()
    return []


def extract_spaces(elem: _Element, xpath: str) -> list[str]:
    """Find an element with xpath and extract a list of space delimited tokens.

    Args:
        elem (_Element): parent element
        xpath (str): xpath location to search

    Returns:
        list[str]: list of tokens
    """
    text = findtext(elem, xpath)
    if text:
        return text.split()
    return []
