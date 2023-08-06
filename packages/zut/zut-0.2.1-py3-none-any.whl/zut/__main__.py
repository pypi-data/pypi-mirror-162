from __future__ import annotations
import argparse
from dotenv import load_dotenv
from .logging import configure_logging
from .command import add_commands, exec_command

load_dotenv()
configure_logging()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

add_commands(subparsers, "zut", include=["credentials"])
add_commands(subparsers, "zut.commands")

exec_command(parser)
