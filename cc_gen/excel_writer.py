from typing import List, Any
from openpyxl import Workbook


class ExcelWriter:
    def __init__(self, filename: str, column_names: List[str]):
        self.filename = filename
        self.column_names = column_names
        self.workbook = None
        self.sheet = None

    def append(self, row: List[Any]):
        self.sheet.append(row)

    def save(self, file: str):
        self.workbook.save(file)

    def num_rows(self) -> int:
        return self.sheet.max_row if self.sheet is not None else 0

    def __enter__(self):
        self.workbook = Workbook()
        self.sheet = self.workbook.active
        self.sheet.append(self.column_names)
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save(self.filename)
