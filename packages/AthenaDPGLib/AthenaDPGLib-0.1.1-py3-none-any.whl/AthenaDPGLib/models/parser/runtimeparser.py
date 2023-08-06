# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import dearpygui.dearpygui as dpg
from dataclasses import dataclass
import json

# Custom Library

# Custom Packages
from AthenaDPGLib.data.runtimeparser_mapping import (
    RUNTIMEPARSER_MAPPING_CONTEXTMANGERS, RUNTIMEPARSER_MAPPING_ITEMS_FULL
)

# ----------------------------------------------------------------------------------------------------------------------
# - Support Code -
# ----------------------------------------------------------------------------------------------------------------------
class Callbacks:
    pass

    def __getitem__(self, item):
        if item in self.__dir__():
            return getattr(self,item)
        else:
            raise ValueError(item)

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True, init=False)
class RuntimeParser:
    filepath:str
    document:dict
    callbacks:Callbacks

    def __init__(self, filepath_input:str, callbacks:Callbacks=None):
        # todo check if the file exists or not
        self.filepath = filepath_input
        self.callbacks = callbacks if callbacks is not None else Callbacks()

    def parse(self):
        """dpg.create_context() has to be run beforehand"""
        with open(self.filepath, "r") as file:
            self.document = json.load(file)

        match self.document["dpg"]:
            case {"mode":"full","_children":children,}:
                self._parse_recursive(parent=children)
            case {"mode":"partial","_children":children,}:
                self._parse_recursive(parent=children)
            case _:
                raise RuntimeError


    def _parse_recursive(self, parent:list):
        for tag, attrib in ((k,v) for item in parent for k, v in item.items()): #type: str, dict
            if tag in RUNTIMEPARSER_MAPPING_CONTEXTMANGERS:
                children = attrib["_children"]
                attrib.pop("_children")
                with RUNTIMEPARSER_MAPPING_CONTEXTMANGERS[tag](**attrib):
                    self._parse_recursive(parent=children)

            elif tag in RUNTIMEPARSER_MAPPING_ITEMS_FULL:
                if "callback" in attrib:
                    attrib["callback"] = self.callbacks[attrib["callback"]]
                RUNTIMEPARSER_MAPPING_ITEMS_FULL[tag](**attrib)

            # for special cases
            elif tag == "primary_window":
                children = attrib["_children"]
                attrib.pop("_children")
                with dpg.window(**attrib, tag="primary_window"):
                    self._parse_recursive(parent=children)
                dpg.set_primary_window("primary_window", True)

            elif tag == "viewport":
                dpg.create_viewport(**attrib)
