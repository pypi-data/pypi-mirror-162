import json
import os
import sys
from typing import Optional

import typer
from termcolor import cprint

from jqlite.filters import Identity, JsonValue
from jqlite.parser import parse


def main():
    typer.run(run)


def run(expr: Optional[str] = typer.Argument(None)):
    f = parse(expr) if expr else Identity()
    json_str = sys.stdin.read()
    json_obj = json.loads(json_str)
    for v in f.input(json_obj):
        if os.isatty(sys.stdout.fileno()):
            json_print(v)
            print()
        else:
            print(json.dumps(v, indent=2))


def json_print(obj: JsonValue, indent=2, level=0):
    if obj is None:
        cprint("null", "cyan", end="")
    elif isinstance(obj, bool):
        cprint(("false", "true")[obj], "yellow", end="")
    elif isinstance(obj, (int, float)):
        cprint(str(obj), "yellow", end="")
    elif isinstance(obj, str):
        cprint(f'"{obj}"', "green", end="")
    elif isinstance(obj, list):
        print("[")
        for i, v in enumerate(obj):
            if i > 0:
                cprint(",")
            print(" " * (level + 1) * indent, end="")
            json_print(v, indent, level + 1)
        print()
        print(" " * level * indent, end="")
        cprint("]", end="")
    elif isinstance(obj, dict):
        print("{")
        for i, (k, v) in enumerate(obj.items()):
            if i > 0:
                cprint(",")
            print(" " * (level + 1) * indent, end="")
            cprint(f'"{k}": ', "blue", end="")
            json_print(v, indent, level + 1)
        print()
        print(" " * level * indent, end="")
        cprint("}", end="")
