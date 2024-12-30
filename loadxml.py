# SPDX-License-Identifier: MIT
# Copyright 2024 Steve Winslow

from lxml import etree

from datatypes import License, NodeType, NodeSpacing, LicenseNode

XHTML_NAMESPACE = "http://www.spdx.org/license"
XHTML = "{%s}" % XHTML_NAMESPACE

# Loads and parses an SPDX License List XML file.
# FIXME extend to handle exceptions as well
# given:   filename: path to License List XML file to load
# returns: datatypes.License or None on failure
def loadLicense(filename):
    # load and parse XML content
    # FIXME handle failure to load file
    tree = etree.parse(filename)
    root = tree.getroot()
    l = parseLicense(root)

    # reload file and save original text
    # FIXME handle failure to load file
    with open(filename, 'r') as f:
        l.origXML = f.read()

    return l

# Parses SPDX License List XML content.
# FIXME extend to handle exceptions as well
# FIXME handle valid XML content that doesn't match ListedLicense schema
# given:   root: lxml etree root node from loaded XML (SPDXLicenseCollection)
# returns: datatypes.License or None on failure
def parseLicense(root):
    l = License()

    licXNode = root.find(f"{XHTML}license")

    # fill in metadata
    l.id = licXNode.get("licenseId")
    l.name = licXNode.get("name")
    osiText = licXNode.get("isOsiApproved", "false")
    l.osi = (osiText == "true")
    l.versionAdded = licXNode.get("listVersionAdded", "")
    l.versionDeprecated = licXNode.get("deprecatedVersion", "")

    crossRefsXNode = licXNode.find(f"{XHTML}crossRefs")
    if crossRefsXNode is not None:
        for crn in crossRefsXNode.getchildren():
            l.crossRefs.append(crn.text)

    notesXNode = licXNode.find(f"{XHTML}notes")
    if notesXNode is not None:
        l.notes = notesXNode.text

    textXNode = licXNode.find(f"{XHTML}text")
    lnode, tailnode = processXMLNode(textXNode)
    l.textNode = lnode
    if tailnode is not None:
        lnode.children.append(tailnode)

    return l

# Processes SPDX License List XML nodes into parsed nodes.
# given:   xmlnode: lxml Element being processed
# returns: lnode: newly created parsed node - LicenseNode
#          tailnode: subsequent node created from this XML node's tail - LicenseNode
def processXMLNode(xmlnode):
    lnode = LicenseNode()
    lnode.lineno = xmlnode.sourceline

    match xmlnode.tag.removeprefix(XHTML):
        case "text":
            lnode.type = NodeType.TOPTEXT
        case "p":
            lnode.type = NodeType.P
        case "titleText":
            lnode.type = NodeType.TITLE
        case "copyrightText":
            lnode.type = NodeType.COPYRIGHT
        case "list":
            lnode.type = NodeType.LIST
        case "item":
            lnode.type = NodeType.ITEM
        case "bullet":
            lnode.type = NodeType.BULLET
        case "br":
            lnode.type = NodeType.BR
        case "optional":
            lnode.type = NodeType.OPTIONAL
            lnode.spacing = _getSpacingAttrib(xmlnode)
        case "alt":
            lnode.type = NodeType.ALT
            lnode.spacing = _getSpacingAttrib(xmlnode)
            lnode.regex = xmlnode.get("match")
            lnode.matchName = xmlnode.get("name")
        case "standardLicenseHeader":
            lnode.type = NodeType.SLHEADER
        case _:
            # FIXME handle invalid tag
            raise ValueError(f"Invalid tag {xmlnode.tag}")

    # currently, process children regardless of whether the node type is
    # actually permitted to have child nodes. do this to pick up text 
    # and tail nodes, including for e.g. <alt> tags.
    children, tailnode = processChildren(xmlnode)
    lnode.children = children

    return lnode, tailnode

def processChildren(xmlnode):
    children = []
    tailnode = None

    # if any text var exists, create a whitespace or text node,
    # depending if we have non-whitespace .text content
    if xmlnode.text is not None:
        if xmlnode.text.strip() == "":
            textnode = _makeWhitespaceNode(xmlnode.sourceline)
        else:
            textnode = _makeTextNode(xmlnode.text, xmlnode.sourceline)
        children.append(textnode)

    # walk through all child nodes and process each
    for c in xmlnode.iterchildren():
        childnode, childTailnode = processXMLNode(c)
        children.append(childnode)
        # FIXME is this the right place to add the child's tail node?
        children.append(childTailnode)

    # if any tail var exists, create a whitespace or text node,
    # depending if we have non-whitespace .tail content
    # NOTE: tail content gets added to this node's _parent's_ children!
    if xmlnode.tail is not None:
        # FIXME BUG - line numbers are incorrect for tail nodes!
        if xmlnode.tail.strip() == "":
            tailnode = _makeWhitespaceNode(xmlnode.sourceline)
        else:
            tailnode = _makeTextNode(xmlnode.tail, xmlnode.sourceline)

    return children, tailnode

# Helper function to create a text node from the specified text string
def _makeTextNode(s, sourceline):
    n = LicenseNode()
    n.type = NodeType.PLAINTEXT
    # retain original whitespace for now, but get starting line number
    # from where non-whitespace character begins
    n.lineno = sourceline + _getPrecedingLineCount(s)
    n.text = s
    return n

# Helper function to create a node representing just whitespace
def _makeWhitespaceNode(sourceline):
    n = LicenseNode()
    n.type = NodeType.WHITESPACE
    n.lineno = sourceline
    return n

# Helper function to extract and return a spacing attribute, accounting
# for default values where not present
def _getSpacingAttrib(xmlnode):
    sptext = xmlnode.get("spacing", None)
    if sptext is None:
        return NodeSpacing.UNSPECIFIED
    match sptext:
        case "before":
            return NodeSpacing.BEFORE
        case "after":
            return NodeSpacing.AFTER
        case "none":
            return NodeSpacing.NONE
        case "both":
            return NodeSpacing.BOTH
        case _:
            return NodeSpacing.INVALID

# Helper function to count the number of whitepace lines preceding
# the first character of non-whitespace content in a string
def _getPrecedingLineCount(s):
    # return 0 if only whitespace present
    if s.strip() == "":
        return 0

    count = 0
    sp = s.splitlines()
    for l in sp:
        if l.strip() != "":
            return count
        count += 1
    return count
