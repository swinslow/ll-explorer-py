# SPDX-License-Identifier: MIT
# Copyright 2024-2025 Steve Winslow

from pprint import pprint

from datatypes import AppData, NodeType, FlatType
from parsexml import loadAllLicenses, loadLicense, flattenLicense
from ui import UI

def printNode(n, indent=0):
    info = n.text
    match n.type:
        case NodeType.OPTIONAL:
            info = f"spacing: {n.spacing}"
        case NodeType.ALT:
            info = f"regex: {n.regex}, name: {n.matchName}, spacing: {n.spacing}"
    print(f"{' '*indent}{n.type} ({n.lineno}): {info}")
    for c in n.children:
        printNode(c, indent+2)

def printXMLAndTextNode():
    lic = loadLicense("/Users/steve/programming/python/testing/lxml/licenses/BSD-3-Clause.xml")
    print("===== LICENSE =====")
    pprint(vars(lic))
    print("===== LICENSE TEXT NODE CONTENTS =====")
    printNode(lic.textNode)

def printFlat(fns, indent=0):
    for fn in fns:
        tail = ""
        match fn.type:
            case FlatType.TEXT:
                tail = f": {fn.text}"
            case FlatType.REGEX:
                tail = f": {fn.regex}"
        print(f"{' '*indent}{fn.type} ({fn.lineno}){tail}")
        if fn.type == FlatType.OPTIONAL:
            printFlat(fn.children, indent+2)

if __name__ == "__main__":
    xmldirpath = "/Users/steve/programming/python/testing/lxml/licenses"
    ad = AppData()
    ad.ui = UI()
    ad.setLicenses(loadAllLicenses(xmldirpath))
    ### FIXME TEMP
    licMIT = ad.lics["MIT"]
    #nodeMIT = licMIT.textNode
    #print(type(nodeMIT))
    #printNode(nodeMIT)
    flattenLicense(licMIT)
    printFlat(licMIT.textFlat)
    ### FIXME END TEMP
    ad.ui.setup(ad)
    ad.ui.run()
