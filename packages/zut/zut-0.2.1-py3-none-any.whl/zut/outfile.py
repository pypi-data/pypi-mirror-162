from __future__ import annotations
import os, sys, csv
from pathlib import Path
from io import IOBase
from tabulate import tabulate

# Register CSV dialect for French version of Excel
class ExcelFr(csv.excel):
    delimiter = ";"

csv.register_dialect('excel-fr', ExcelFr())

class open_outfile:
    def __init__(self, target: str|Path|IOBase = None, append: bool = False, newline: str = None, encoding: str = None, csv_dialect: str = None, **kwargs):
        self.append = append
        self.newline = newline
        self.encoding = encoding
        self.csv_dialect = csv_dialect

        # Update target
        self.opened = False
        self.file: IOBase = None
        self.strpath: str = None
        if not target or target == "stdout":
            self.file = sys.stdout
        elif target == "stderr":
            self.file = sys.stderr
        elif isinstance(target, IOBase):
            self.file = target
        elif isinstance(target, Path):
            self.strpath = str(target)
        elif isinstance(target, str):
            self.strpath = target
        else:
            raise AttributeError(f"target: invalid type {type(target).__name__}")

        # For CSV file:
        # - Set newline to '', otherwise newlines embedded inside quoted fields will not be interpreted correctly. See footnote of: https://docs.python.org/3/library/csv.html
        # - Set encoding to utf-8-sig (UTF8 with BOM): CSV is for exchanges, encoding should not depend on the exporting operating system. BOM is necessary for correct display with Excel
        if (self.strpath and self.strpath.lower().endswith(".csv")) or self.csv_dialect:
            if self.newline is None:
                self.newline = ''
            if self.encoding is None:
                self.encoding = 'utf-8-sig'

        # Handle strpath
        if self.strpath:
            # Replace "{key}" in path by keyword arguments
            for key, value in kwargs.items():
                self.strpath = self.strpath.replace("{"+key+"}", value)
        else:
            if hasattr(self.file, "name"):
                self.strpath = self.file.name
            if not self.strpath:
                self.strpath = f"<{type(self.file).__name__}>"

    def __enter__(self):
        if not self.file:
            self.opened = True
            Path(self.strpath).parent.mkdir(parents=True, exist_ok=True)
            self.file = open(self.strpath, "a" if self.append else "w", newline=self.newline, encoding=self.encoding)
        return self

    def __exit__(self, *args):
        if self.opened:
            self.file.close()
        elif self.headers or self.rows:
            print(tabulate(self.rows, headers=self.headers), file=self.file)

    def __str__(self) -> str:
        return self.strpath

    # -------------------------------------------------------------------------
    # For tabular data
    # -------------------------------------------------------------------------

    @property
    def headers(self):
        if not hasattr(self, "_headers"):
            return None
        return self._headers
        
    @headers.setter
    def headers(self, data: list):
        self._headers = data
        if self.opened:
            self.csv_writer.writerow(data)
        # else: will be handled in exit method by tabulate

    @property
    def rows(self):
        if not hasattr(self, "_rows"):
            self._rows = []
        return self._rows

    def append_row(self, data: list):
        self.rows.append(data)
        if self.opened:
            self.csv_writer.writerow(data)
        # else: will be handled in exit method by tabulate

    @property
    def csv_writer(self):
        if not hasattr(self, "_csv_writer"):
            dialect = os.environ.get("CSV_DIALECT", self.csv_dialect)
            if not dialect:
                dialect = "excel-fr"
            self._csv_writer = csv.writer(self.file, dialect=dialect)
        return self._csv_writer
