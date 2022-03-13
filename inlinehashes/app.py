"""CLI App.

This file contains all the logic for the command line interface of
this library. It makes use of the same tools available for those that
install the package in order to be used programatically.
"""
from typing import List
import requests
import argparse
import inlinehashes
import json


def build_output(
    inlines: List[inlinehashes.lib.Inline], alg: str, full: bool = False
) -> str:
    """Build a JSON output from a list of Inline objects."""
    snippet = "content" if full else "short_content"
    out = [{"content": getattr(i, snippet), "hash": getattr(i, alg)} for i in inlines]
    return json.dumps(out, indent=2)


def write_to_file(path: str, content: str) -> None:
    """Writes the content to the specified file.

    raises:
        OSError: More than one subclass of OSError
    """
    with open(path, "w") as f:
        f.write(content)


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
    parser.add_argument("-o", "--output", help="Store output in a file.")
    args = parser.parse_args()
    path = args.source

    try:
        if path.startswith("http://") or path.startswith("https://"):
            response = requests.get(path)
            response.raise_for_status()
            content = response.text
        else:
            with open(path, "r") as f:
                content = f.read()
    except (requests.RequestException, OSError):
        print(f"Invalid source: {path}")
        exit(1)

    inlines = inlinehashes.parse(content)
    out = build_output(inlines, args.alg, bool(args.full))

    if args.output:
        write_to_file(args.output, out)
    else:
        print(out)


if __name__ == "__main__":
    run_cli()
