#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tkinter
from tkinter import W, filedialog, ttk, E
from typing import Optional, List

from .formatter_and_parser import is_none_or_empty


def __ask_path(title: str, old_path: str, filetypes: Optional[List[str]]):
    if filetypes is None:
        new_path = filedialog.askdirectory(
            initialdir=os.path.dirname(old_path),
            title=title
        )
    else:
        filetypes_name = " ".join(filetypes) + " files"
        filetypes_value = " ".join(list(map(lambda x: "." + x, filetypes)))
        new_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(old_path),
            title=title,
            filetypes=[(filetypes_name, filetypes_value)]
        )

    if not is_none_or_empty(new_path) and new_path != '' and new_path != old_path:
        return new_path.replace('/', '\\')

    return None


def create_general_path_picker(frame: tkinter.Frame,
                               row: int,
                               old_path: str,
                               btn_title: str,
                               filetypes: Optional[List[str]],
                               on_changed: Optional[any] = None,
                               btn_width=30,
                               label_width=90,
                               pad=5
                               ):
    old_path = '' if old_path is None else old_path

    content = tkinter.StringVar(value=old_path)

    message = ttk.Entry(frame, width=label_width, textvariable=content, style='TLabel', justify='right',
                        state='readonly')
    message.grid(padx=pad, pady=pad, row=row, column=1, columnspan=3, sticky=E + W)

    def on_btn_click():
        new_path = __ask_path(btn_title, old_path, filetypes)
        if new_path is not None:
            content.set(new_path)
            if on_changed is not None:
                on_changed(new_path, old_path)

    btn = tkinter.Button(frame, width=btn_width, text=btn_title, command=on_btn_click)
    btn.grid(padx=pad, pady=pad, row=row, column=0, columnspan=1, sticky=E + W)

    return btn, message
