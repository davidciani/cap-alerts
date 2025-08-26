from datetime import datetime

import pyparsing as pp
from lxml.etree import _Element

from cap_alerts import NS_MAP

class IPAWSAlertsError(Exception):
    """Base class for custom exceptions in this module."""
    pass

class Malformed(IPAWSAlertsError):
    """Specific exception class."""
    def __init__(self, message, detail):
        super().__init__(message)
        self.detail = detail

def convint(st: str) -> int:
    try:
        return int(st)
    except ValueError:  # If you get a ValueError
        return int(float(st))


def formatTime(self, record, datefmt=None):
    return (
        datetime.fromtimestamp(record.created)
        .astimezone()
        .isoformat(timespec="milliseconds")
    )


def find(elem: _Element, xpath: str) -> _Element | None:
    return elem.find(xpath, namespaces=NS_MAP)


def findtext(elem: _Element, xpath: str) -> str | None:
    return elem.findtext(xpath, namespaces=NS_MAP)


def findall(elem: _Element, xpath: str) -> list[_Element]:
    return elem.findall(xpath, namespaces=NS_MAP)


def findint(elem: _Element, xpath) -> int | None:
    return convint(x) if (x := findtext(elem, xpath)) is not None else None


def findalltext(elem: _Element, xpath: str) -> list[str]:
    return [x.text for x in findall(elem, xpath) if x.text is not None]


quoted_str_parser = pp.OneOrMore(
    pp.QuotedString(quote_char='"') | pp.Word(pp.printables, exclude_chars='"')
)


def extract_quoted(elem: _Element, xpath: str) -> list[str]:
    text = findtext(elem, xpath)
    if text:
        results = quoted_str_parser.parse_string(text)
        return results.as_list()
    else:
        return []

def extract_spaces(elem: _Element, xpath: str) -> list[str]:
    text = findtext(elem, xpath)
    if text:
        return text.split()
    else:
        return []