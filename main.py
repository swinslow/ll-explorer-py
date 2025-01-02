# SPDX-License-Identifier: MIT
# Copyright 2024 Steve Winslow

from pprint import pprint

from datatypes import AppData, NodeType
from loadxml import loadAllLicenses, loadLicense
from ui import UI

def printNode(n, indent=0):
    info = n.text
    match n.type:
        case NodeType.OPTIONAL:
            info = f"spacing: {n.spacing}"
        case NodeType.ALT:
            info = f"regex: {n.regex}, name: {n.matchName}, spacing: {n.spacing}"
    print(f"{" "*indent}{n.type} ({n.lineno}): {info}")
    for c in n.children:
        printNode(c, indent+2)

def printXMLAndTextNode():
    lic = loadLicense("/Users/steve/programming/python/testing/lxml/licenses/BSD-3-Clause.xml")
    print("===== LICENSE =====")
    pprint(vars(lic))
    print("===== LICENSE TEXT NODE CONTENTS =====")
    printNode(lic.textNode)

if __name__ == "__main__":
    xmldirpath = "/Users/steve/programming/python/testing/lxml/licenses"
    ad = AppData()
    ad.ui = UI()
    ad.setLicenses(loadAllLicenses(xmldirpath))
    ad.ui.setup(ad)
    ad.ui.run()
