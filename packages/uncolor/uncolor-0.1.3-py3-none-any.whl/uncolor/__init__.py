"""Strips ANSI colors from a data stream on standard input."""

import fileinput
import re


def uncolor() -> None:
    # https://stackoverflow.com/a/14693789
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    for line in fileinput.input():
        print(ansi_escape.sub("", line), end="")
