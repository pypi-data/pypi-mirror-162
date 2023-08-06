"""Define a command-line interface for the module.
Call parse_args() to return an argument parser namespace.
"""
import argparse


def parse_args() -> argparse.Namespace:
    """Define an argument parser and return the parsed arguments."""
    parser = argparse.ArgumentParser(
        prog="uncolor",
        description="strips ANSI colors from a data stream",
    )

    return parser.parse_args()
