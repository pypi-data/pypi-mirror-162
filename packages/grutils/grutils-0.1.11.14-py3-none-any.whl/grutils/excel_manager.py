#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from shutil import copy
from typing import Dict, Optional
from .error import Error
from .excel import is_excel_file_opened, sheet_with_name, close_wb, quit_app
from .file import should_exists
import xlwings as xw
from .formatter_and_parser import is_none_or_empty


class ExcelFilesManager:
    def __init__(self, visible=True, add_book=False):
        self.excel_app = xw.App(visible=visible, add_book=add_book)
        self.excel_app.display_alerts = False
        self.opened_excel_files: Dict[str, xw.Book] = {}

    def close_opened_excel_file(self, file_path: str, save_changes: bool = True):
        if file_path in self.opened_excel_files:
            wb = self.opened_excel_files[file_path]
            if save_changes:
                wb.save(file_path)
            close_wb(wb)

            self.opened_excel_files.pop(file_path)

    def release(self):
        for file_path in self.opened_excel_files:
            wb = self.opened_excel_files[file_path]
            close_wb(wb)

        self.opened_excel_files.clear()
        quit_app(self.excel_app)

    def get_excel_book(self, err: Error,
                       file_path: str,
                       multi_reading: bool = True):
        if file_path in self.opened_excel_files:
            return self.opened_excel_files[file_path]

        if not should_exists(err, file_path):
            return

        if not multi_reading and is_excel_file_opened(file_path):
            err.append("{} is opened, please close it and try again".format(file_path))
            return

        wb = self.excel_app.books.open(file_path, update_links=False)
        self.opened_excel_files[file_path] = wb

        return wb

    def get_excel_sheet(self, err: Error,
                        file_path: str,
                        sheet_name: Optional[str] = None,
                        multi_reading: bool = True):
        wb: xw.Book = self.get_excel_book(err, file_path, multi_reading)
        if err.has_error():
            return

        if is_none_or_empty(sheet_name):
            sht: xw.Sheet = wb.sheets[0]
        else:
            sht = sheet_with_name(err, wb, name=sheet_name)

        return None if err.has_error() else sht

    def create_excel_file(self, err: Error, file_path: str, template_file_path: Optional[str] = None):
        try:
            if template_file_path is None:
                wb = self.excel_app.books.add()
                wb.save(file_path)
                self.opened_excel_files[file_path] = wb
            else:
                copy(template_file_path, file_path)
                self.get_excel_book(err, file_path, False)
        except Exception as e:
            err.append('create new excel file as {} failed with error {}'.format(file_path, e))
