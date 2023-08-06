from __future__ import annotations
import sys, shlex, argparse
from typing import Callable
from pathlib import Path
from importlib import import_module
from importlib.util import find_spec
from .format import FOREGROUND_RED

_parser = None

def add_commands(parser: argparse.ArgumentParser, package_name: str, include: list[str]=[], exclude: list[str]=[]):
    global _parser

    if isinstance(parser, argparse.ArgumentParser):
        _parser = parser
        subparsers = parser.add_subparsers()
    else:
        # parser is assumed to be subparsers
        subparsers = parser

    package_spec = find_spec(package_name)
    if not package_spec:
        raise KeyError(f"package not found: {package_name}")
    if not package_spec.origin:
        raise KeyError(f"not a package: {package_name} (did you forget __init__.py ?)")
    package_path = Path(package_spec.origin).parent
    
    for module_path in package_path.iterdir():
        if module_path.is_dir() or module_path.name.startswith("_") or not module_path.name.endswith(".py"):
            continue

        module_name = module_path.stem
        if include and not module_name in include:
            continue
        if exclude and module_name in exclude:
            continue

        module = import_module(f"{package_name}.{module_name}")

        handle = getattr(module, "handle")
        add_arguments = getattr(module, "add_arguments", None)
        help = getattr(module, "HELP", None)

        subparser = subparsers.add_parser(module_name, help=help, description=help) # help: in list of commands, description: in command help
        subparser.set_defaults(func=handle)
        if add_arguments:
            add_arguments(subparser)

    return subparsers


def exec_command(parser: ArgumentParser, default: Callable = None):
    args = vars(parser.parse_args())
    func = args.pop("func", None)
    if not func:
        if default:
            func = default
        else:
            print(FOREGROUND_RED % "missing command name")
            sys.exit(2)

    r = func(**args)
    if not isinstance(r, int):
        r = 0
    sys.exit(r)


def run_command(cmd: str|list, parser: argparse.ArgumentParser = None):
    if not parser:
        if not _parser:
            raise ValueError("parser not provided")
        parser = _parser

    cmd = [str(arg) for arg in cmd] if isinstance(cmd, list) else shlex.split(cmd)

    try:
        args = vars(parser.parse_args(cmd))
    except SystemExit:
        raise ValueError(f"cannot run command {cmd}")

    func = args.pop("func", None)
    if not func:
        raise ValueError("missing command name")

    return func(**args)
