#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter import W, END, ttk, E


def create_log_view(frame: tkinter.Frame, row: int, initial_content: str = '', height=30):
    row += 1
    logs_view = tkinter.Text(frame, height=height)
    logs_view.grid(padx=5, pady=5, row=row, column=0, columnspan=4, sticky=E + W)
    logs_view_scrollbar = ttk.Scrollbar(frame, command=logs_view.yview)
    logs_view_scrollbar.grid(row=row, column=6, sticky='nsew')
    logs_view['yscrollcommand'] = logs_view_scrollbar.set
    append_log(logs_view, initial_content)
    return logs_view


def append_log(logs_view: tkinter.Text, log: str, is_err: bool = False):
    if logs_view is None:
        return

    logs_view.insert(END, log + '\n')

    # auto scroll to bottom
    logs_view.see(END)
    if is_err:
        set_logs_color(logs_view, 'red')


def clear_logs(logs_view: tkinter.Text):
    if logs_view is None:
        return
    logs_view.delete(1.0, END)
    set_logs_color(logs_view, 'white')


def set_logs_color(logs_view: tkinter.Text, color: str = 'white'):
    if logs_view is None:
        return
    logs_view.config(background=color)

