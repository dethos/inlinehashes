"""CLI App.

This file contains all the logic for the command line interface of
this library. It makes use of the same tools available for those that
install the package in order to be used programatically.
"""
from typing import List
from urllib.request import urlopen, Request
from urllib.error import URLError
import argparse
import inlinehashes
import json


def build_output(
    inlines: List[inlinehashes.lib.Inline], alg: str, full: bool = False
) -> str:
    """Build a JSON output from a list of Inline objects."""
    snippet = "content" if full else "short_content"
    out = [
        {
            "content": getattr(i, snippet),
            "hash": getattr(i, alg),
            "line": i.line,
            "position": i.position,
        }
        for i in inlines
    ]
    return json.dumps(out, indent=2)


def run_cli() -> None:
    """Entry point of the command line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="URL or local HTML file to check")
    parser.add_argument(
        "-a",
        "--alg",
        help="Hash algorithm to use (default: sha256)",
        default="sha256",
        choices=["sha256", "sha384", "sha512"],
    )
    parser.add_argument(
        "-f",
        "--full",
        help="Include full content in the output",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--target",
        help="Target inline content to look for",
        default="all",
        choices=["all", "scripts", "styles"],
    )
    args = parser.parse_args()
    path = args.source
    target = args.target

    try:
        if path.startswith("http://") or path.startswith("https://"):
            req = Request(
                path,
                headers={"User-Agent": f"Inlinehashes[{inlinehashes.__version__}]"},
            )
            with urlopen(req) as response:
                content = response.read()
        else:
            with open(path, "r") as f:
                content = f.read()
    except (URLError, OSError) as error:
        print(error)
        print(f"Failed to get source: {path}")
        exit(1)

    inlines = inlinehashes.parse(content, target)
    out = build_output(inlines, args.alg, bool(args.full))
    print(out)


if __name__ == "__main__":
    run_cli()
