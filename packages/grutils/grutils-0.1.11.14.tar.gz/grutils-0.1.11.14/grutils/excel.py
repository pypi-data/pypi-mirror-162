#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
from typing import List, Union, Callable, Optional
import xlwings as xw
from xlwings.utils import rgb_to_int
from .error import Error
from .form import Form


def sheet_with_name(err: Error, wb: xw.Book, name='sheet name'):
    if err.has_error():
        return None
    for sht in wb.sheets:
        if sht.name == name:
            return sht

    err.append('excel file({}) has no sheet named "{}"'.format(wb.fullname, name))
    return None


def count_of_continue_none_cells(items: List[any] = None):
    if items is None:
        items = []
    i = len(items) - 1
    count = 0
    while i >= 0:
        if items[i] is None:
            count += 1
        else:
            break
        i -= 1
    return count


def row_items(err: Error, sht: xw.Sheet, row=1, first_column='A', last_column='IV'):
    if err.has_error():
        return None
    range_str = '{}{}:{}{}'.format(first_column, row, last_column, row)
    r = sht.range(range_str)
    cells = r.value

    count = count_of_continue_none_cells(cells)
    return cells[0:len(cells) - count]


def merge_area_value(err: Error, sht: xw.Sheet, merge_area: xw.Range):
    if err.has_error():
        return

    first_cell_str = "{}{}".format(num_to_column(merge_area.column), merge_area.row)
    return sht.range(first_cell_str).value


def rows_items(err: Error, sht: xw.Sheet, start_row=1, end_row=2, first_column='A', last_column='IV',
               fill_merged_cells_at_right: bool = True, fill_merged_cells_at_bottom: bool = False):
    if err.has_error():
        return

    if start_row > end_row or start_row < 1:
        err.append("invalid parameter start_row \'{}\' and end_row \'{}\'".format(start_row, end_row))
        return

    # get rows cells
    range_str = '{}{}:{}{}'.format(first_column, start_row, last_column, end_row)
    r = sht.range(range_str)
    rows: List[List] = r.value if start_row != end_row else [r.value]

    # get merged areas
    merge_areas: List = []
    start_column_num = column_to_num(first_column)
    max_column_num = start_column_num
    for row_num, row_cells in enumerate(rows, start_row):
        for column_num, cell in enumerate(row_cells, start_column_num):
            if cell is not None:
                cell_range = sht.range('{}{}'.format(num_to_column(column_num), row_num))
                cell_merge_area = cell_range.merge_area
                last_cell_merge_area = cell_merge_area.last_cell

                if last_cell_merge_area.column > max_column_num:
                    max_column_num = last_cell_merge_area.column
                if cell_range == cell_merge_area:
                    continue

                merge_area = {
                    "value": cell,
                    "start_row_num": row_num,
                    "start_column_num": column_num,
                    "end_row_num": last_cell_merge_area.row,
                    "end_column_num": last_cell_merge_area.column,
                    "start_row_index": row_num - start_row,
                    "start_column_index": column_num - start_column_num,
                    "end_row_index": last_cell_merge_area.row - start_row,
                    "end_column_index": last_cell_merge_area.column - start_column_num
                }
                merge_areas.append(merge_area)

    # fill merged cells
    if fill_merged_cells_at_right or fill_merged_cells_at_bottom:
        for merge_area in merge_areas:
            value = merge_area["value"]
            start_row_index = merge_area["start_row_index"]
            start_column_index = merge_area["start_column_index"]
            end_row_index = merge_area["end_row_index"]
            end_column_index = merge_area["end_column_index"]
            if fill_merged_cells_at_right and not fill_merged_cells_at_bottom:
                for column_index in range(start_column_index, end_column_index + 1):
                    if column_index < len(rows[start_row_index]):
                        rows[start_row_index][column_index] = value
            elif not fill_merged_cells_at_right and fill_merged_cells_at_bottom:
                for row_index in range(start_row_index, end_row_index + 1):
                    if row_index < len(rows):
                        rows[row_index][start_column_index] = value
            else:
                for row_index in range(start_row_index, end_row_index + 1):
                    if row_index < len(rows):
                        for column_index in range(start_column_index, end_column_index + 1):
                            if column_index < len(rows[row_index]):
                                rows[row_index][column_index] = value

    # remove useless cells in row
    column_count = max_column_num - start_column_num + 1
    rows = list(map(lambda row: row[0:column_count], rows))

    return rows


def row_items_with_column(err: Error, sht: xw.Sheet, row=1, first_column='A', last_column='IV'):
    items = row_items(err, sht, row, first_column, last_column)
    results = []
    i = 0
    for item in items:
        results.append((add_column(first_column, i), item))
        i += 1

    return results


def row_items_filtered(err: Error, sht: xw.Sheet, tester=lambda x: True, row=1, first_column='A', last_column='IV'):
    items = row_items_with_column(err, sht, row, first_column, last_column)
    if tester is None:
        return items

    results = filter(lambda x: tester(x[1]), items)
    return list(results)


def column_items_sub(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    if err.has_error():
        return []
    end_row = start_row + steps - 1
    if type(column) == str:
        range_str = '{}{}:{}{}'.format(column, start_row, column, end_row)
        return sht.range(range_str).value
    else:
        return sht.range((start_row, column), (end_row, column)).value


def column_items(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    if err.has_error():
        return []

    items = []
    start_row_sub = start_row
    count = count_of_continue_none_cells(items)
    while count < steps:
        items = items + column_items_sub(err, sht, column, start_row_sub, steps)
        start_row_sub += steps
        count = count_of_continue_none_cells(items)

    return items[0:len(items) - count]


def column_items_with_row(err: Error, sht: xw.Sheet, column='A', start_row=1, steps=100):
    items = column_items(err, sht, column, start_row, steps)
    results = []
    i = 0
    for item in items:
        results.append((start_row + i, item))
        i += 1

    return results


def column_items_filtered(err: Error, sht: xw.Sheet, tester=lambda x: True, column='A', start_row=1, steps=100):
    items = column_items_with_row(err, sht, column, start_row, steps)
    if tester is None:
        return items

    results = filter(lambda x: tester(x[1]), items)
    return list(results)


def num_to_column(num: int):
    if num < 0:
        s = 'column number({}) is less than 0'.format(num)
        raise Exception(s)
    elif num == 0:
        return ""
    elif num <= 26:
        return chr(65 - 1 + num)

    right = num % 26
    if right == 0:
        right = 26
    left = int((num - right) / 26)
    return num_to_column(left) + num_to_column(right)


def column_to_num(column: str):
    length = len(column)
    if length == 0:
        return 0
    elif length == 1:
        num = ord(column.upper()) - ord('A') + 1
        if num < 1 or num > 26:
            s = 'column char({}) is not in a~z, or A~Z'.format(column)
            raise Exception(s)
        return num
    else:
        return 26 * column_to_num(column[0:length - 1]) + column_to_num(column[length - 1:])


def add_column(column: str, add_num: int):
    num = column_to_num(column)
    return num_to_column(num + add_num)


def close_wb(wb: xw.Book):
    if wb is not None:
        wb.close()


def quit_app(app: xw.App):
    if app is not None:
        app.quit()


def orange_red():
    return rgb_to_int((255, 69, 0))


def banana_yellow():
    return rgb_to_int((227, 207, 87))


def sky_blue():
    return rgb_to_int((135, 206, 235))


def green():
    return rgb_to_int((0, 255, 0))


def is_excel_file_opened(file_path: str):
    (file_folder, file_name) = os.path.split(file_path)

    locked_file = file_folder + '\\~$' + file_name
    return os.path.exists(locked_file)


def append_sht_to_another(err: Error, source_wb: xw.Book, target_wb: xw.Book,
                          source_sheet: str = 'Sheet1',
                          target_sheet: str = 'Sheet1',
                          skip_if_no_source_sheet: bool = False,
                          empty_rows: int = 1,
                          source_ref_column: str = 'A',
                          target_ref_column: str = 'A',
                          source_start_row: int = 1,
                          target_start_row: int = 1,
                          steps=100, end_col='IV'):
    if err.has_error():
        return
    source_sht = sheet_with_name(err, source_wb, source_sheet)
    if err.has_error():
        if skip_if_no_source_sheet:
            print('[Info] skip to copy sheet "{}", because it is not exists'.format(source_sheet))
            err.clear()
            return
        return

    source_row_count = len(column_items(err, source_sht, source_ref_column, start_row=source_start_row, steps=steps))
    if err.has_error():
        return

    if source_row_count == 0:
        return

    target_sht = sheet_with_name(err, target_wb, target_sheet)
    if err.has_error():
        return
    target_row_count = len(column_items(err, target_sht, target_ref_column, start_row=target_start_row, steps=steps))
    if err.has_error():
        return

    source_range = source_sht.range('A{}:{}{}'.format(source_start_row, end_col,
                                                      source_start_row + source_row_count - 1))
    split_row_count = 0 if target_row_count == 0 else empty_rows

    _target_start_row = target_start_row - 1 + target_row_count + 1 + split_row_count
    _target_end_row = target_start_row - 1 + target_row_count + source_row_count + split_row_count
    target_range = target_sht.range('A{}:{}{}'.format(_target_start_row, end_col, _target_end_row))
    source_range.copy(target_range)
    return True


def upload_data_to_another_file(err: Error,
                                app: xw.App,
                                source_file_path: str,
                                target_file_path: str,
                                source_sheet: str = 'Sheet1',
                                target_sheet: str = 'Sheet1',
                                empty_rows: int = 1,
                                source_ref_column: str = 'A',
                                target_ref_column: str = 'A'
                                ):
    if err.has_error():
        return

    # check target folder is exists
    target_folder = os.path.dirname(target_file_path)
    if not os.path.exists(target_folder):
        err.append('try to upload data to shared file {}, but its folder {} is not exists'
                   .format(target_file_path, target_folder))
        return

    # check file opening
    opened = is_excel_file_opened(target_file_path)
    if opened:
        err.append('try to upload data to shared file {}, but it is opened now'.format(target_file_path))
        return

    # copy file if target is not exists
    if not os.path.exists(target_file_path):
        try:
            shutil.copy(source_file_path, target_file_path)
            target_wb: xw.Book = app.books.open(target_file_path, update_links=False)

            # rename sheet if should
            if source_sheet != target_sheet:
                target_sht = sheet_with_name(err, target_wb, source_sheet)
                if err.has_error():
                    close_wb(target_wb)
                    return
                target_sht.name = target_sheet
                target_wb.save()

            # remove useless sheets
            has_useless_sheets = False
            for sht in target_wb.sheets:
                if sht.name != target_sheet:
                    has_useless_sheets = True
                    sht.delete()
            if has_useless_sheets:
                target_wb.save()

            close_wb(target_wb)

        except Exception as e:
            err.append(
                'copy file {} to file {} failed with error {}'.format(source_file_path, target_file_path, e))
        return

    # uploading
    source_wb = app.books.open(source_file_path, update_links=False)
    target_wb = app.books.open(target_file_path, update_links=False)

    uploaded = append_sht_to_another(err, source_wb, target_wb,
                                     source_sheet,
                                     target_sheet,
                                     False,
                                     empty_rows,
                                     source_ref_column,
                                     target_ref_column)

    if uploaded is not None and uploaded:
        target_wb.save()

    close_wb(source_wb)
    close_wb(target_wb)


def get_blocks_from_sheet(err: Error, sht: xw.Sheet,
                          block_mark_tester: Union[str, Callable[[any], bool]],
                          block_mark_col='A',
                          block_title_row_ref_num=0,
                          block_start_col='A',
                          start_row=1,
                          steps=100,
                          do_smart_repair_title=True,
                          block_end_col='IV',
                          ):
    if err.has_error():
        return

    # find block mark rows
    items = column_items_with_row(err, sht, column=block_mark_col, start_row=start_row, steps=steps)
    if err.has_error():
        return

    def __tester(x):
        match = block_mark_tester(x) if type(block_mark_tester) != str else '{}'.format(x) == block_mark_tester
        return match

    mark_column_cells = list(filter(lambda x: __tester(x[1]), items))
    blocks_count = len(mark_column_cells)
    if blocks_count == 0:
        msg = 'cannot find any block marked in column \'{}\' with start row \'{}\''.format(block_mark_col, start_row)
        err.append(msg)
        return

    # read block one by one
    last_row_num = items[-1][0]
    blocks: List[Form] = []
    for i in range(blocks_count):
        mark_cell = mark_column_cells[i]
        block_mark_row_num, mark_value = mark_cell
        block_title_row_num = block_mark_row_num + block_title_row_ref_num
        form = Form(err)

        # check block content rows count
        block_end_row_num = last_row_num if i == blocks_count - 1 else mark_column_cells[i + 1][0] - 1
        block_row_count = block_end_row_num - block_title_row_num + 1
        if block_row_count < 2:
            msg = 'block at row \'{}\' is empty or only contains title row' \
                .format(block_mark_row_num)
            err.append(msg)
            return

        # read block title
        block_title_cells = row_items(err, sht, block_title_row_num, block_start_col, last_column=block_end_col)
        if err.has_error():
            return

        if len(block_title_cells) == 0:
            msg = 'title row of block at row \'{}\' is empty' \
                .format(block_mark_row_num)
            err.append(msg)
            return

        form.set_title_row(block_title_row_num, block_title_cells,
                           do_smart_repair_title=do_smart_repair_title)

        block_end_col = num_to_column(column_to_num(block_start_col) + len(block_title_cells) - 1)

        # read block content
        for j in range(block_row_count - 1):
            row_num = block_title_row_num + 1 + j
            phase_content_row_range_str = "{}{}:{}{}".format(block_start_col, row_num, block_end_col, row_num)
            cells = sht.range(phase_content_row_range_str).value

            form.append_data_row(row_num, cells)

        # save form
        if err.has_error():
            return

        blocks.append(form)

    return None if err.has_error() else blocks


def build_row_range(row_num: int, end_col='IV'):
    return 'A{}:{}{}'.format(row_num, end_col, row_num)


def copy_excel_row(source_sht: xw.Sheet, source_row_num: int,
                   target_sht: xw.Sheet, target_row_num: int,
                   with_content: bool = False, end_col='IV'):
    source_range = build_row_range(source_row_num, end_col)
    target_range = build_row_range(target_row_num, end_col)
    source_sht.range(source_range).copy(target_sht.range(target_range))
    if not with_content:
        target_sht.range(target_range).clear_contents()


def read_sht_bottom_row(err: Error, sht: xw.Sheet,
                        ref_cols: Optional[List[str]] = None,
                        steps=100):
    if err.has_error():
        return

    if ref_cols is None:
        ref_cols = ['A', 'B', 'C', 'D']

    max_row_num = 1
    for col in ref_cols:
        column_cells = column_items(err, sht, col, steps=steps)
        if err.has_error():
            return
        max_row_num = max(len(column_cells), max_row_num)

    return max_row_num


def read_sht_rightest_col(err: Error, sht: xw.Sheet,
                          ref_rows: Optional[List[int]] = None, last_column='IV'):
    if err.has_error():
        return

    if ref_rows is None:
        ref_rows = [1, 2, 3]

    max_col_num = 1
    for row in ref_rows:
        row_cells = row_items(err, sht, row, last_column=last_column)
        if err.has_error():
            return
        max_col_num = max(len(row_cells), max_col_num)

    return max_col_num
