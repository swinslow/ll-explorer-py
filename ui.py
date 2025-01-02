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
        self.root.title = "SPDX License List Explorer"

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

    # Update list of licenses from AppData
    def updateLics(self):
        if self.licenseIDVar is None and self.root is not None:
            self.licenseIDVar = StringVar()
        if self.licenseIDVar is not None:
            self.licenseIDVar.set(sorted(self.appdata.lics.keys()))

    # Run user interface
    def run(self):
        self.root.mainloop()
