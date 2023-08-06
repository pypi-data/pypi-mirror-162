import sys
from typing import Optional

import typer
import json

from jqlite.filters import Identity
from jqlite.parser import parse


def run(expr: Optional[str] = typer.Argument(None)):
    f = parse(expr) if expr else Identity()
    json_str = sys.stdin.read()
    json_obj = json.loads(json_str)
    for v in f.input(json_obj):
        print(json.dumps(v, indent=2))


def main():
    typer.run(run)


if __name__ == "__main__":
    main()
