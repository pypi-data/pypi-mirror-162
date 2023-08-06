#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Tuple, Union
from .excel import rows_items, num_to_column, column_to_num, column_items
from .formatter_and_parser import is_none_or_empty, string_of
from .error import Error
import xlwings as xw
from .form import Form


def remove_unfilled_rows(err: Error, form: Form, must_not_empty_fields: List[str]):
    if err.has_error():
        return

    field_indexes: List[int] = list(map(lambda x: form.column_index_with_title(x), must_not_empty_fields))
    if err.has_error():
        return

    unfilled_row_indexes: List[int] = []
    for row_index in range(len(form.data_rows)):
        row = form.data_rows[row_index]
        for field_index in field_indexes:
            cell_val = row.cell(field_index, err)
            if is_none_or_empty(cell_val):
                unfilled_row_indexes.insert(0, row_index)
                break

    for row_index in unfilled_row_indexes:
        form.data_rows.pop(row_index)


def read_sht_headers(err: Error, sht: xw.Sheet, header_start_row=1, header_end_row=1,
                     start_col: str = 'A',
                     fill_merged_cells_at_right: bool = True,
                     fill_merged_cells_at_bottom: bool = False,
                     header_joiner: str = "", end_col='IV'):
    if err.has_error():
        return

    # get title rows
    rows = rows_items(err, sht, header_start_row, header_end_row, start_col,
                      last_column=end_col,
                      fill_merged_cells_at_right=fill_merged_cells_at_right,
                      fill_merged_cells_at_bottom=fill_merged_cells_at_bottom)
    if err.has_error():
        return

    # join multi row cells as title in each column
    row_count = len(rows)
    column_count = len(rows[0]) if row_count > 0 else 0
    if column_count == 0:
        return
    headers: List[str] = []
    for column_index in range(column_count):
        columns = list(map(lambda row: row[column_index], rows))
        columns = list(filter(lambda column: not is_none_or_empty(column), columns))
        columns = list(map(lambda column: string_of(column), columns))

        header = header_joiner.join(columns)
        headers.append(header)
    return headers


def read_sht(err: Error, sht: xw.Sheet, ref_col: str = 'A', header_row: Union[int, Tuple[int, int]] = 1,
             start_col: str = 'A',
             fill_merged_cells_at_right: bool = True,
             fill_merged_cells_at_bottom: bool = False,
             header_joiner: str = "",
             steps=100,
             do_smart_repair_title=True, end_col='IV'):
    if err.has_error():
        return

    # get headers
    _header_row: Tuple[int, int] = (header_row, header_row) if type(header_row) == int else header_row
    header_start_row, header_end_row = _header_row

    headers = read_sht_headers(err, sht, header_start_row, header_end_row,
                               start_col,
                               fill_merged_cells_at_right,
                               fill_merged_cells_at_bottom,
                               header_joiner, end_col=end_col)

    if err.has_error():
        return

    # add titles to form
    end_col = num_to_column(column_to_num(start_col) + len(headers) - 1)
    form = Form(err)
    form.set_title_row(header_start_row, headers,
                       do_smart_repair_title=do_smart_repair_title)

    # add data rows to form
    cells_col = column_items(err, sht, ref_col, header_end_row + 1, steps=steps)
    for i in range(len(cells_col)):
        row_num = header_end_row + 1 + i
        cells = sht.range("{}{}:{}{}".format(start_col, row_num, end_col, row_num)).value
        form.append_data_row(row_num, cells)

    return form
