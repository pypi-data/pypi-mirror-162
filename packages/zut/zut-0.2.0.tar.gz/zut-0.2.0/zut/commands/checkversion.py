from __future__ import annotations
from importlib import import_module
from ..git import check_git_version_tags

def add_arguments(parser):
    parser.add_argument("--module", action="store", default="setup", help="the module containing VERSION attribute")

def handle(module: str):
    importedmodule = import_module(module)
    
    version = getattr(importedmodule, "VERSION")
    if not check_git_version_tags(version):
        return 1
