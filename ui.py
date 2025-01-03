# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

from tkinter import *
from tkinter import ttk

class UI:
    def __init__(self):
        super(UI, self).__init__()

        # Application data
        self.appdata = None

        # StringVar-ified copy of license IDs, generated from appdata.lics
        self.licenseIDVar = None

        # Tk root window
        self.root = None

        # primary frame in root window
        self.c = None

        # license IDs listbox and scrollbar
        self.licids = None
        self.licidsys = None

        # StringVar for selected license ID
        self.licSelectedID = None

        # license XML, license ID label and scrollbars
        self.licxml = None
        self.licxmllbl = None
        self.licxmlys = None
        self.licxmlxs = None

        # processed and flattened XML and scrollbars
        self.licflat = None
        self.licflatys = None
        self.licflatxs = None

    def setup(self, appdata):
        # set up Tk root window
        self.root = Tk()
        self.root.title("SPDX License List Explorer")

        # set up application data and list of licenses
        self.appdata = appdata
        self.updateLics()

        # set up root window overall frame
        self.c = ttk.Frame(self.root, padding="5 5 12 0")
        self.c.grid(column=0, row=0, sticky=(N, W, E, S))

        # set up UI for list of license IDs
        self.licids = Listbox(self.c, height=20, width=30,
                              listvariable=self.licenseIDVar,
                              selectmode="browse")
        self.licids.grid(column=0, row=1, sticky=(N, W, E, S))
        self.licidsys = ttk.Scrollbar(self.c, orient=VERTICAL,
                                      command=self.licids.yview)
        self.licidsys.grid(column=1, row=1, sticky=(N, S))
        self.licids.configure(yscrollcommand=self.licidsys.set)

        ttk.Separator(self.c, orient=VERTICAL).grid(
                column=2, row=0, rowspan=3, sticky=(N,S))

        # set up UI for license XML content
        self.licSelectedID = StringVar()
        self.licxmllbl = ttk.Label(self.c, textvariable=self.licSelectedID)
        self.licxml = Text(self.c, width=100, height=50, wrap="none")
        self.licxmlys = ttk.Scrollbar(self.c, orient=VERTICAL,
                                      command=self.licxml.yview)
        self.licxmlxs = ttk.Scrollbar(self.c, orient=HORIZONTAL,
                                      command=self.licxml.xview)
        self.licxml["yscrollcommand"] = self.licxmlys.set
        self.licxml["xscrollcommand"] = self.licxmlxs.set
        self.licxml["state"] = "disabled"

        self.licxmllbl.grid(column=3, row=0, sticky=(E,W), columnspan=2)
        self.licxml.grid(column=3, row=1, sticky=(N,S,E,W))
        self.licxmlys.grid(column=4, row=1, sticky=(N,S))
        self.licxmlxs.grid(column=3, row=2, sticky=(E,W))

        # configure weights for grid resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.c.columnconfigure(3, weight=1)
        self.c.columnconfigure(6, weight=1)
        self.c.rowconfigure(1, weight=1)

        # FIXME note that the rest should maybe be pulled into separate function

        # set up alternating listbox colors
        alternate = False
        for i in range(len(self.appdata.lics)):
            if alternate:
                self.licids.itemconfigure(i, background="#f0f0ff")
            alternate = not alternate

        # set up selection bindings
        self.licids.bind("<<ListboxSelect>>",
                         lambda e: self.selectId(self.licids.curselection()))

    # Update list of licenses from AppData
    # FIXME this logic is unnecessarily complex and should be cleaned up
    def updateLics(self):
        if self.licenseIDVar is None and self.root is not None:
            self.licenseIDVar = StringVar()
        if self.licenseIDVar is not None:
            self.licenseIDVar.set(sorted(self.appdata.lics.keys(), key=str.casefold))
        # FIXME probably also change licSelectedID

    # Callback: Selected license ID from self.licids listbox
    def selectId(self, selection):
        self.licxml["state"] = "normal"
        # FIXME according to TkDocs tutorial, since licids has "browse" for
        # FIXME its selectmode, curselection should always be length 1
        if len(selection) == 1:
            i = selection[0]

            # clear existing text
            self.licxml.delete('1.0', 'end')

            # set selection
            licid = sorted(self.appdata.lics.keys(), key=str.casefold)[i]
            self.licSelectedID.set(licid)
            self.licxml.insert('1.0', self.appdata.lics[licid].origXML)

        self.licxml["state"] = "disabled"


    # Run user interface
    def run(self):
        self.root.mainloop()
