# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

from tkinter import *
from tkinter import ttk

from lltokenize import TextPreprocessorConfig, TextPreprocessor

class DebugUI:
    def __init__(self):
        super(DebugUI, self).__init__()

        ##### UI ELEMENTS #####

        # debug toplevel window (note: NOT root window, see ui.py)
        self.window = None

        # notebook for varying debug tabs
        self.notebook = None

        # primary frame for text preproc debug view
        self.frameDebug = None

        # orig text view, label and scrollbars
        self.origtext = None
        self.origlbl = None
        self.origys = None
        self.origxs = None

        # proc text view, label and scrollbars
        self.proctext = None
        self.proclbl = None
        self.procys = None
        # no horizontal scrollbar b/c we want the tokens to wrap

        # convert orig => proc button
        self.convertbtn = None

        # clear orig and proc button
        self.clearbtn = None

        ##### TEXT PROCESSING DATA #####

        # text preprocessor config and system
        self.tpcfg = TextPreprocessorConfig()
        self.tp = TextPreprocessor(self.tpcfg)

    def setup(self, root):
        # set up debug Toplevel (not root) window, using root reference
        self.window = Toplevel(root)
        self.window.title("Debug window")

        # set up notebook tabs
        self.notebook = ttk.Notebook(self.window)
        self._setupFrameDebug()

        # configure weights for grid resizing
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

    def _setupFrameDebug(self):
        self.frameDebug = ttk.Frame(self.notebook, padding="5 5 12 0")
        self.notebook.add(self.frameDebug, text="Text Processing")

        # set up original text widgets
        self.origlbl = ttk.Label(self.frameDebug, text="original")
        self.origtext = Text(self.frameDebug, width=80, height=40, wrap="none")
        self.origys = ttk.Scrollbar(self.frameDebug, orient=VERTICAL,
                                    command=self.origtext.yview)
        self.origxs = ttk.Scrollbar(self.frameDebug, orient=HORIZONTAL,
                                    command=self.origtext.xview)
        self.origtext["yscrollcommand"] = self.origys.set
        self.origtext["xscrollcommand"] = self.origxs.set

        self.origlbl.grid(column=0, row=0, sticky=(E,W))
        self.origtext.grid(column=0, row=1, sticky=(N,S,E,W))
        self.origys.grid(column=1, row=1, sticky=(N,S))
        self.origxs.grid(column=0, row=2, sticky=(E,W))

        # set up processed text widgets
        self.proclbl = ttk.Label(self.frameDebug, text="processed")
        self.proctext = Text(self.frameDebug, width=80, height=40)
        self.procys = ttk.Scrollbar(self.frameDebug, orient=VERTICAL,
                                    command=self.proctext.yview)
        self.proctext["yscrollcommand"] = self.procys.set
        self.proctext["state"] = "disabled"

        self.proclbl.grid(column=3, row=0, sticky=(E,W))
        self.proctext.grid(column=3, row=1, sticky=(N,S,E,W))
        self.procys.grid(column=4, row=1, sticky=(N,S))

        # set up convert and clear buttons
        self.convertbtn = ttk.Button(self.frameDebug, text="Convert >",
                                     command=self.textProcConvert)
        self.convertbtn.grid(column=2, row=1, sticky=(E,W))
        self.clearbtn = ttk.Button(self.frameDebug, text="Clear",
                                     command=self.textProcClear)
        self.clearbtn.grid(column=2, row=2, sticky=(E,W))

        # configure weights for grid resizing
        self.frameDebug.columnconfigure(0, weight=1)
        self.frameDebug.rowconfigure(1, weight=1)

        self.notebook.grid()

    ##### TEXT PROCESSING FUNCTIONS #####

    def textProcConvert(self, *args):
        self.tp.process(self.origtext.get("1.0", "end"))
        self.proctext["state"] = "normal"
        self.proctext.delete("1.0", "end")
        self.proctext.insert("1.0", self.tp.proc)
        self.proctext["state"] = "disabled"

    def textProcClear(self, *args):
        self.origtext.delete("1.0", "end")
        self.proctext["state"] = "normal"
        self.proctext.delete("1.0", "end")
        self.proctext["state"] = "disabled"
