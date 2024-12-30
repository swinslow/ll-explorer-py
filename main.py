# SPDX-License-Identifier: MIT
# Copyright 2024 Steve Winslow

from pprint import pprint

from datatypes import NodeType
from loadxml import loadLicense

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

if __name__ == "__main__":
    lic = loadLicense("/Users/steve/programming/python/testing/lxml/licenses/BSD-3-Clause.xml")
    print("===== LICENSE =====")
    pprint(vars(lic))
    print("===== LICENSE TEXT NODE CONTENTS =====")
    printNode(lic.textNode)
