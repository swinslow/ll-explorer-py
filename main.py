# SPDX-License-Identifier: MIT
# Copyright 2024-2025 Steve Winslow

from pprint import pprint

from datatypes import AppData, NodeType, FlatType
from parsexml import XMLParserConfig, XMLParser
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

def tempFlatten(parser, ad, licId):
    lic = ad.lics[licId]
    #node = lic.textNode
    #print(type(node))
    #printNode(node)
    parser.flatten(lic)
    printFlat(lic.textFlat)

if __name__ == "__main__":
    xmldirpath = "/Users/steve/programming/python/testing/lxml/licenses"
    cfg = XMLParserConfig()
    parser = XMLParser(cfg)

    ad = AppData()
    ad.ui = UI()
    ad.setLicenses(parser.loadAll(xmldirpath))
    ### FIXME TEMP
    #tempFlatten(parser, ad, "MIT")
    ### FIXME END TEMP
    ad.ui.setup(ad)
    ad.ui.run()
