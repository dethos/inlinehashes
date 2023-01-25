"""CLI App.

This file contains all the logic for the command line interface of
this library. It makes use of the same tools available for those that
install the package in order to be used programatically.
"""
import argparse
import json
from typing import List
from urllib.error import URLError
from urllib.request import Request, urlopen

from rich import box
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

import inlinehashes


def build_json_output(inlines: List[inlinehashes.lib.Inline], alg: str) -> Syntax:
    """Build a JSON output from a list of Inline objects."""
    out = [
        {
            "content": i.short_content,
            "hash": getattr(i, alg),
            "directive": i.directive,
            "line": i.line,
            "position": i.position,
        }
        for i in inlines
    ]
    return Syntax(json.dumps(out, indent=2), "JSON", theme="ansi_dark")


def build_plain_output(inlines: List[inlinehashes.lib.Inline], alg: str) -> str:
    """Build a simple output of an inline per line."""
    return "\n".join(
        [
            f"[magenta]{i.directive}[/magenta] [cyan]{i.line}[/cyan] "
            f"[green]{i.position}[/green] [default]{getattr(i, alg)}[/default]"
            for i in inlines
        ]
    )


def build_table_output(inlines: List[inlinehashes.lib.Inline], alg: str) -> Table:
    """Build a table to output the inlines in a nicer way."""
    table = Table(box=box.HORIZONTALS)
    table.add_column("Directive", style="magenta")
    table.add_column("Line", justify="right", style="cyan")
    table.add_column("Position", justify="right", style="green")
    table.add_column("Hash")

    for i in inlines:
        table.add_row(i.directive, str(i.line), str(i.position), getattr(i, alg))

    return table


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
        "-o",
        "--output",
        help="Format used to write the output (default: table)",
        default="table",
        choices=["table", "json", "plain"],
    )
    parser.add_argument(
        "-t",
        "--target",
        help="Target inline content to look for (default: all)",
        default="all",
        choices=["all", "script-src", "style-src"],
    )
    args = parser.parse_args()
    path = args.source
    target = args.target
    output_format = args.output
    console = Console()

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
        console.print(error)
        console.print(f"Failed to get source: {path}")
        exit(1)

    inlines = inlinehashes.parse(content, target)
    if output_format == "json":
        console.print(build_json_output(inlines, args.alg))
    elif output_format == "plain":
        console.print(build_plain_output(inlines, args.alg))
    else:
        console.print(build_table_output(inlines, args.alg))


if __name__ == "__main__":
    run_cli()
