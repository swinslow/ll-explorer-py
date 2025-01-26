# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

from tkinter import *
from tkinter import ttk

from lltokenize import TextPreprocessorConfig, TextPreprocessor

PADDING_COORDS = "5 5 12 0"

class DebugUI:
    def __init__(self):
        super(DebugUI, self).__init__()

        ##### DEBUG UI ELEMENTS #####

        # debug toplevel window (note: NOT root window, see ui.py)
        self.window = None

        # notebook for varying debug tabs
        self.notebook = None

        ##### TEXT PROCESSING WIDGETS #####

        # primary frame for text preproc debug view
        self.cDebugTP = None

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

        ##### LICENSE TOKENIZING WIDGETS #####

        # primary frame for license tokens debug view
        self.cDebugToken = None

        # dict of license ID => datatypes.License
        # set with call to setLicenses() so that the UI components
        # can be notified of changes, if UI has been loaded!
        self.tokenLics = {}

        # license IDs listbox and scrollbar
        self.tokenLicIDs = None
        self.tokenLicIDsys = None

        # license XML, license ID label and scrollbars
        self.tokenLicXML = None
        self.tokenLicXMLlbl = None
        self.tokenLicXMLys = None
        self.tokenLicXMLxs = None

        # processed and flattened XML and scrollbars
        self.tokenLicFlat = None
        self.tokenLicFlatys = None
        self.tokenLicFlatxs = None

        # StringVar-ified copy of license IDs, generated from lics
        self.tokenLicenseIDVar = None

        # StringVar for selected license ID
        self.tokenLicSelectedIDVar = None

        ##### LICENSE TOKENIZING DATA #####

    ##### MAIN UI SETUP #####

    def setup(self, root, lics):
        # set up debug Toplevel (not root) window, using root reference
        self.window = Toplevel(root)
        self.window.title("Debug window")

        # set up notebook tabs
        self.notebook = ttk.Notebook(self.window)
        self._setupFrameTP()
        self._setupFrameToken(lics)

        self.notebook.grid()

        # configure weights for grid resizing
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

##### TEXT PROCESSING UI SETUP #####

    def _setupFrameTP(self):
        self.cDebugTP = ttk.Frame(self.notebook, padding=PADDING_COORDS)
        self.notebook.add(self.cDebugTP, text="Text Processing")

        # set up original text widgets
        self.origlbl = ttk.Label(self.cDebugTP, text="original")
        self.origtext = Text(self.cDebugTP, width=80, height=40,
                             wrap="none", undo=True)
        self.origys = ttk.Scrollbar(self.cDebugTP, orient=VERTICAL,
                                    command=self.origtext.yview)
        self.origxs = ttk.Scrollbar(self.cDebugTP, orient=HORIZONTAL,
                                    command=self.origtext.xview)
        self.origtext["yscrollcommand"] = self.origys.set
        self.origtext["xscrollcommand"] = self.origxs.set

        self.origlbl.grid(column=0, row=0, sticky=(E,W))
        self.origtext.grid(column=0, row=1, sticky=(N,S,E,W))
        self.origys.grid(column=1, row=1, sticky=(N,S))
        self.origxs.grid(column=0, row=2, sticky=(E,W))

        # set up processed text widgets
        self.proclbl = ttk.Label(self.cDebugTP, text="processed")
        self.proctext = Text(self.cDebugTP, width=80, height=40)
        self.procys = ttk.Scrollbar(self.cDebugTP, orient=VERTICAL,
                                    command=self.proctext.yview)
        self.proctext["yscrollcommand"] = self.procys.set
        self.proctext["state"] = "disabled"

        self.proclbl.grid(column=3, row=0, sticky=(E,W))
        self.proctext.grid(column=3, row=1, sticky=(N,S,E,W))
        self.procys.grid(column=4, row=1, sticky=(N,S))

        # set up convert and clear buttons
        self.convertbtn = ttk.Button(self.cDebugTP, text="Convert >",
                                     command=self._textProcConvert)
        self.convertbtn.grid(column=2, row=1, sticky=(E,W))
        self.clearbtn = ttk.Button(self.cDebugTP, text="Clear",
                                     command=self._textProcClear)
        self.clearbtn.grid(column=2, row=2, sticky=(E,W))

        # configure weights for grid resizing
        self.cDebugTP.columnconfigure(0, weight=1)
        self.cDebugTP.rowconfigure(1, weight=1)

    ##### TEXT PROCESSING FUNCTIONS #####

    def _textProcConvert(self, *args):
        self.tp.process(self.origtext.get("1.0", "end"))
        self.proctext["state"] = "normal"
        self.proctext.delete("1.0", "end")
        self.proctext.insert("1.0", self.tp.proc)
        self.proctext["state"] = "disabled"

    def _textProcClear(self, *args):
        self.origtext.delete("1.0", "end")
        self.proctext["state"] = "normal"
        self.proctext.delete("1.0", "end")
        self.proctext["state"] = "disabled"

    ##### LICENSE TOKENIZING UI SETUP #####

    def _setupFrameToken(self, lics):
        self._setTokenLicenses(lics)

        self.cDebugToken = ttk.Frame(self.notebook, padding=PADDING_COORDS)
        self.notebook.add(self.cDebugToken, text="License Tokens")

        # set up license IDs listbox
        self.tokenLicIDs = Listbox(self.cDebugToken, height=20, width=30,
                                   listvariable=self.tokenLicenseIDVar,
                                   selectmode="browse")
        self.tokenLicIDs.grid(column=0, row=1, sticky=(N, W, E, S))
        self.tokenLicIDsys = ttk.Scrollbar(self.cDebugToken, orient=VERTICAL,
                                           command=self.tokenLicIDs.yview)
        self.tokenLicIDsys.grid(column=1, row=1, sticky=(N, S))
        self.tokenLicIDs.configure(yscrollcommand=self.tokenLicIDsys.set)

        ttk.Separator(self.cDebugToken, orient=VERTICAL).grid(
            column=2, row=0, rowspan=3, sticky=(N, S))

        # set up UI for license XML content
        self.tokenLicSelectedIDVar = StringVar()
        self.tokenLicXMLlbl = ttk.Label(self.cDebugToken,
                                        textvariable=self.tokenLicSelectedIDVar)
        self.tokenLicXML = Text(self.cDebugToken,
                                width=90, height=50, wrap="none")
        self.tokenLicXMLys = ttk.Scrollbar(self.cDebugToken, orient=VERTICAL,
                                      command=self.tokenLicXML.yview)
        self.tokenLicXMLxs = ttk.Scrollbar(self.cDebugToken, orient=HORIZONTAL,
                                      command=self.tokenLicXML.xview)
        self.tokenLicXML["yscrollcommand"] = self.tokenLicXMLys.set
        self.tokenLicXML["xscrollcommand"] = self.tokenLicXMLxs.set
        self.tokenLicXML["state"] = "disabled"

        self.tokenLicXMLlbl.grid(column=3, row=0, sticky=(E,W), columnspan=2)
        self.tokenLicXML.grid(column=3, row=1, sticky=(N,S,E,W))
        self.tokenLicXMLys.grid(column=4, row=1, sticky=(N,S))
        self.tokenLicXMLxs.grid(column=3, row=2, sticky=(E,W))

        ttk.Separator(self.cDebugToken, orient=VERTICAL).grid(
            column=5, row=0, rowspan=3, sticky=(N, S))

        # configure weights for grid resizing
        self.cDebugToken.columnconfigure(3, weight=1)
        self.cDebugToken.rowconfigure(1, weight=1)

        # FIXME note that the rest should maybe be pulled into separate function

        self._updateTokenLics()

        # set up alternating listbox colors
        alternate = False
        for i in range(len(self.tokenLics)):
            if alternate:
                self.tokenLicIDs.itemconfigure(i, background="#f0f0ff")
            alternate = not alternate

        # set up selection bindings
        self.tokenLicIDs.bind("<<ListboxSelect>>",
            lambda e: self._selectTokenLicId(self.tokenLicIDs.curselection()))

    ##### LICENSE TOKENIZING FUNCTIONS #####

    def _setTokenLicenses(self, lics):
        self.tokenLics = lics
        self._updateTokenLics()

    # Update list of licenses from self.tokenLics
    # FIXME this logic is unnecessarily complex and should be cleaned up
    def _updateTokenLics(self):
        if self.tokenLicenseIDVar is None and self.window is not None:
            self.tokenLicenseIDVar = StringVar()
        if self.tokenLicenseIDVar is not None:
            self.tokenLicenseIDVar.set(
                sorted(self.tokenLics.keys(), key=str.casefold))
        # FIXME probably also change tokenLicSelectedIDVar

    # Callback: Selected license ID from self.tokenLicIDs listbox
    def _selectTokenLicId(self, selection):
        self.tokenLicXML["state"] = "normal"
        # FIXME according to TkDocs tutorial, since licids has "browse" for
        # FIXME its selectmode, curselection should always be length 1
        if len(selection) == 1:
            i = selection[0]

            # clear existing text
            self.tokenLicXML.delete('1.0', 'end')

            # set selection
            licid = sorted(self.tokenLics.keys(), key=str.casefold)[i]
            self.tokenLicSelectedIDVar.set(licid)
            self.tokenLicXML.insert('1.0', self.tokenLics[licid].origXML)

        self.tokenLicXML["state"] = "disabled"
