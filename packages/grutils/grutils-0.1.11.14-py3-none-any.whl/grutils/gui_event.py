#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Optional


class GUIEvent:
    def __init__(self, category: str, name: str, key: Optional[str] = None, val: any = None):
        self.category = category
        self.name = name
        self.payload: Dict[str, any] = {}
        if key is not None and val is not None:
            self.payload[key] = val

    def add_property(self, k: str, v: any):
        self.payload[k] = v
        return self

    def __repr__(self):
        s = "\nGUI Event<\n"
        s += "category: {}\n".format(self.category)
        s += "name: {}\n".format(self.name)
        s += "payload: {}\n".format(self.payload)
        s += ">\n"
        return s

    def __str__(self):
        return self.__repr__()
