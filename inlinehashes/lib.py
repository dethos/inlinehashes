"""Inline Hashes - Helping with CSP when possible.

This small module helps you to parse HTML documents and extract all the inline
content that must be specifically allowed in the Content-Security-Policy in
order to work (assuming "unsafe-inline" is not present).
"""
from typing import List
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
import hashlib
import base64

from bs4 import BeautifulSoup

_VALID_TARGETS = {
    "scripts": [
        {"name": "script"},
    ],
    "styles": [
        {"name": "style"},
    ],
}


@dataclass(frozen=True)
class Inline:
    """Represents a piece of content present in the HTML document.

    It can be the value of an element/node or the value of an attribute
    of a given element/node.
    """

    content: str

    @cached_property
    def short_content(self) -> str:
        return self.content[:50]

    @cached_property
    def sha256(self) -> str:
        h = hashlib.sha256(self.content.encode("utf-8"))
        h_b64 = base64.b64encode(h.digest()).decode("utf8")
        return f"sha256-{h_b64}"

    @cached_property
    def sha384(self) -> str:
        h = hashlib.sha384(self.content.encode("utf-8"))
        h_b64 = base64.b64encode(h.digest()).decode("utf8")
        return f"sha384-{h_b64}"

    @cached_property
    def sha512(self) -> str:
        h = hashlib.sha512(self.content.encode("utf-8"))
        h_b64 = base64.b64encode(h.digest()).decode("utf8")
        return f"sha512-{h_b64}"

    def __repr__(self) -> str:
        return f"Inline(content='{self.content}')"

    def __str__(self) -> str:
        return f"Inline(content='{self.short_content}...')"


def parse(content: str, target: str = "all") -> List[Inline]:
    """Parses an HTML document and extracts."""
    soup = BeautifulSoup(content, "html.parser")

    if target == "all":
        search_queries = chain(*_VALID_TARGETS.values())
    elif target in _VALID_TARGETS.keys():
        search_queries = _VALID_TARGETS[target]
    else:
        raise ValueError("Invalid Target")

    elements = []
    for q in search_queries:
        elements += soup.find_all(**q)

    return [Inline(e.contents[0]) for e in elements if e.contents]
