"""Inline Hashes - Helping with CSP when possible.

This small module helps you to parse HTML documents and extract all the inline
content that must be specifically allowed in the Content-Security-Policy in
order to work (assuming "unsafe-inline" is not present).
"""
import base64
import hashlib
from dataclasses import dataclass
from functools import cached_property, partial
from itertools import chain
from typing import Callable, List, Optional

from bs4 import BeautifulSoup, Tag  # type: ignore


@dataclass(frozen=True)
class SearchQuery:
    search_function: Callable
    attr_name: Optional[str]
    directive: str


@dataclass(frozen=True)
class Inline:
    """Represents a piece of content present in the HTML document.

    It can be the value of an element/node or the value of an attribute
    of a given element/node.
    """

    content: str
    directive: Optional[str] = None
    line: Optional[int] = None
    position: Optional[int] = None

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
        return f"Inline(line='{self.line}', position='{self.position}')"

    def __str__(self) -> str:
        return self.content


def matches_attribute(tag: Tag, attribute_name: str) -> bool:
    return tag.has_attr(attribute_name)


def matches_name(tag: Tag, name: str) -> bool:
    return tag.name == name


_EVENT_HANDLER_ATTRS = [
    "onafterprint",
    "onafterscriptexecute",
    "onanimationcancel",
    "onanimationend",
    "onanimationiteration",
    "onanimationstart",
    "onauxclick",
    "onbeforecopy",
    "onbeforecut",
    "onbeforeprint",
    "onbeforescriptexecute",
    "onbeforeunload",
    "onbegin",
    "onblur",
    "onbounce",
    "oncanplay",
    "oncanplaythrough",
    "onchange",
    "onclick",
    "onclose",
    "oncontextmenu",
    "oncopy",
    "oncuechange",
    "oncut",
    "ondblclick",
    "ondrag",
    "ondragend",
    "ondragenter",
    "ondragleave",
    "ondragover",
    "ondragstart",
    "ondrop",
    "ondurationchange",
    "onend",
    "onended",
    "onerror",
    "onfocusin",
    "onfocusout",
    "onfullscreenchange",
    "onhashchange",
    "oninput",
    "oninvalid",
    "onkeydown",
    "onkeypress",
    "onkeyup",
    "onload",
    "onloadeddata",
    "onloadedmetadata",
    "onloadend",
    "onloadstart",
    "onmessage",
    "onmousedown",
    "onmouseenter",
    "onmouseleave",
    "onmousemove",
    "onmouseout",
    "onmouseover",
    "onmouseup",
    "onmousewheel",
    "onmozfullscreenchange",
    "onpagehide",
    "onpageshow",
    "onpaste",
    "onpause",
    "onplay",
    "onplaying",
    "onpointerdown",
    "onpointerenter",
    "onpointerleave",
    "onpointermove",
    "onpointerout",
    "onpointerover",
    "onpointerrawupdate",
    "onpointerup",
    "onpopstate",
    "onprogress",
    "onrepeat",
    "onreset",
    "onresize",
    "onscroll",
    "onsearch",
    "onseeked",
    "onseeking",
    "onselect",
    "onselectionchange",
    "onselectstart",
    "onshow",
    "onstart",
    "onsubmit",
    "ontoggle",
    "ontouchend",
    "ontouchmove",
    "ontouchstart",
    "ontransitioncancel",
    "ontransitionend",
    "ontransitionrun",
    "ontransitionstart",
    "onunhandledrejection",
    "onunload",
    "onvolumechange",
    "onwebkitanimationend",
    "onwebkitanimationiteration",
    "onwebkitanimationstart",
    "onwebkittransitionend",
    "onwheel",
]

_VALID_TARGETS = {
    "script-src": [
        SearchQuery(partial(matches_name, name="script"), None, "script-src"),
        *[
            SearchQuery(
                partial(matches_attribute, attribute_name=attr), attr, "script-src"
            )
            for attr in _EVENT_HANDLER_ATTRS
        ],
    ],
    "style-src": [
        SearchQuery(partial(matches_name, name="style"), None, "style-src"),
        SearchQuery(
            partial(matches_attribute, attribute_name="style"), "style", "style-src"
        ),
    ],
}


def parse(content: str, target: str = "all") -> List[Inline]:
    """Parses an HTML document and extracts."""
    soup = BeautifulSoup(content, "html.parser")

    if target == "all":
        search_queries = chain(*_VALID_TARGETS.values())
    elif target in _VALID_TARGETS.keys():
        search_queries = chain(_VALID_TARGETS[target])
    else:
        raise ValueError("Invalid Target")

    elements = []
    for q in search_queries:
        for tag in soup.find_all(q.search_function):
            if q.attr_name:
                inline = Inline(
                    tag[q.attr_name],
                    q.directive,
                    tag.sourceline,
                    tag.sourcepos,
                )
            else:
                if not tag.contents:
                    continue
                inline = Inline(
                    tag.contents[0],
                    q.directive,
                    tag.sourceline,
                    tag.sourcepos,
                )
            elements.append(inline)
    return elements
