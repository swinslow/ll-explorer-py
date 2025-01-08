# SPDX-License-Identifier: MIT
# Copyright 2024-2025 Steve Winslow

import os

from lxml import etree

from datatypes import License, NodeType, NodeSpacing, LicenseNode, \
        LicenseFlat, FlatType

XHTML_NAMESPACE = "http://www.spdx.org/license"
XHTML = "{%s}" % XHTML_NAMESPACE

class XMLParserConfig:
    def __init__(self):
        super(XMLParserConfig, self).__init__()

        # should an unspecified spacing attribute be treated as "before"
        # (per the schema's default), as "none" (as many of the actual
        # license XML files appear to treat things), or another option?
        self.defaultSpacing = NodeSpacing.BEFORE

        # should adjacent flat whitespace nodes at the same level (e.g., 
        # not counting those under children of optional nodes) be
        # collapsed into a single whitespace node?
        self.mergeWhitespace = True

        # should leading / trailing whitespace in flattened text nodes
        # be converted to separate whitespace nodes?
        self.replaceTextWhitespace = True

        # regardless replaceTextWhitespace, should we _remove_ whitespace
        # nodes if the preceding or subsequent node is an optional or
        # regex flat node with a spacing value that indicates no spacing?
        self.removeConflictingWhitespace = True

class XMLParser:
    def __init__(self, cfg):
        super(XMLParser, self).__init__()

        # XML loader configuration object
        self.cfg = cfg

    # Loads and parses all SPDX License List XML files in the specified
    # directory (non-recursively).
    # given:   dirpath: path to directory containing License List XML files
    # returns: dict of license ID => datatypes.License
    def loadAll(self, dirpath):
        lics = {}
        xmlfiles = sorted(os.listdir(dirpath))
        for xmlfile in xmlfiles:
            xmlpath = os.path.join(dirpath, xmlfile)
            if os.path.isfile(xmlpath) and os.path.splitext(xmlpath)[1] == ".xml":
                lic = self.load(xmlpath)
                lics[lic.id] = lic
        return lics

    # Loads and parses an SPDX License List XML file.
    # FIXME extend to handle exceptions as well
    # given:   filename: path to License List XML file to load
    # returns: datatypes.License or None on failure
    def load(self, filename):
        # load and parse XML content
        # FIXME handle failure to load file
        tree = etree.parse(filename)
        root = tree.getroot()
        l = self.parse(root)

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
    def parse(self, root):
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
        lnode, tailnode = self.processXMLNode(textXNode)
        l.textNode = lnode
        if tailnode is not None:
            lnode.children.append(tailnode)

        return l

    # Processes SPDX License List XML nodes into parsed nodes.
    # given:   xmlnode: lxml Element being processed
    # returns: lnode: newly created parsed node - LicenseNode
    #          tailnode: subsequent node created from this XML node's
    #                    tail - LicenseNode
    def processXMLNode(self, xmlnode):
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
                lnode.spacing = self._getSpacingAttrib(xmlnode)
            case "alt":
                lnode.type = NodeType.ALT
                lnode.spacing = self._getSpacingAttrib(xmlnode)
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
        children, tailnode = self.processChildren(xmlnode)
        lnode.children = children

        return lnode, tailnode

    def processChildren(self, xmlnode):
        children = []
        tailnode = None

        # if any text var exists, create a whitespace or text node,
        # depending if we have non-whitespace .text content
        if xmlnode.text is not None:
            if xmlnode.text.strip() == "":
                textnode = self._makeWhitespaceNode(xmlnode.sourceline)
            else:
                textnode = self._makeTextNode(xmlnode.text, xmlnode.sourceline)
            children.append(textnode)

        # walk through all child nodes and process each
        for c in xmlnode.iterchildren():
            childnode, childTailnode = self.processXMLNode(c)
            children.append(childnode)
            # FIXME is this the right place to add the child's tail node?
            children.append(childTailnode)

        # if any tail var exists, create a whitespace or text node,
        # depending if we have non-whitespace .tail content
        # NOTE: tail content gets added to this node's _parent's_ children!
        if xmlnode.tail is not None:
            # FIXME BUG - line numbers are incorrect for tail nodes!
            if xmlnode.tail.strip() == "":
                tailnode = self._makeWhitespaceNode(xmlnode.sourceline)
            else:
                tailnode = self._makeTextNode(xmlnode.tail, xmlnode.sourceline)

        return children, tailnode

    # Helper function to create a text node from the specified text string
    def _makeTextNode(self, s, sourceline):
        n = LicenseNode()
        n.type = NodeType.PLAINTEXT
        # retain original whitespace for now, but get starting line number
        # from where non-whitespace character begins
        n.lineno = sourceline + self._getPrecedingLineCount(s)
        n.text = s
        return n

    # Helper function to create a node representing just whitespace
    def _makeWhitespaceNode(self, sourceline):
        n = LicenseNode()
        n.type = NodeType.WHITESPACE
        n.lineno = sourceline
        return n

    # Helper function to extract and return a spacing attribute, accounting
    # for default values where not present
    def _getSpacingAttrib(self, xmlnode):
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
    def _getPrecedingLineCount(self, s):
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

    # Creates a flattened version of the specified License's textNode.
    # given:   lic: License to flatten
    def flatten(self, lic):
        flats = []
        if lic.textNode.type != NodeType.TOPTEXT:
            raise RuntimeError(f"expected NodeType.TOPTEXT, got {lic.textNode.type}")
        self._flattenChildren(lic.textNode, flats)
        lic.textFlat = flats

    def _flattenChildren(self, t, flats):
        for c in t.children:
            match c.type:
                case NodeType.PLAINTEXT:
                    # create a flat text token
                    self._addFlatsText(c, flats)
                case (NodeType.P |
                      NodeType.LIST |
                      NodeType.ITEM |
                      NodeType.SLHEADER):
                    # for each of these, flatten its children
                    self._flattenChildren(c, flats)
                case NodeType.BULLET:
                    # FIXME insert better bullet regex with lookahead.
                    # FIXME need lookahead b/c otherwise this will grab
                    # FIXME the first word of the next text bit, if the
                    # FIXME bullet is absent from the text being matched
                    self._addFlatsRegex(c, flats, "\\S{0,7}")
                case NodeType.COPYRIGHT:
                    # FIXME insert with lookahead
                    # FIXME consider whether spacing="both" is correct here
                    self._addFlatsRegex(c, flats, ".*", NodeSpacing.BOTH)
                case NodeType.ALT:
                    # FIXME insert with possible lookahead
                    self._addFlatsRegex(c, flats, c.regex, c.spacing)
                case NodeType.TITLE:
                    # FIXME consider whether spacing="both" is correct here
                    self._addFlatsOptional(c, flats, NodeSpacing.BOTH)
                case NodeType.OPTIONAL:
                    self._addFlatsOptional(c, flats, c.spacing)
                case NodeType.BR:
                    pass
                case NodeType.WHITESPACE:
                    self._addFlatsWhitespace(c, flats)
                case _:
                    raise RuntimeError(f"expected valid NodeType, got {c.type} for line {c.lineno}")

    def _addFlatsText(self, c, flats):
        lf = LicenseFlat()
        lf.type = FlatType.TEXT
        lf.lineno = c.lineno
        lf.text = c.text
        flats.append(lf)

    def _addFlatsWhitespace(self, c, flats):
        lf = LicenseFlat()
        lf.type = FlatType.WHITESPACE
        lf.lineno = c.lineno
        flats.append(lf)

    def _addFlatsRegex(self, c, flats, regex, spacing):
        # FIXME for regex, consider whether spacing should be added as
        # FIXME new whitespace nodes, or as additions to the regex itself

        # add spacing before if applicable
        # FIXME decide whether to treat UNSPECIFIED as equivalent to BEFORE
        if spacing in [NodeSpacing.BEFORE, NodeSpacing.BOTH, NodeSpacing.UNSPECIFIED]:
            self._addFlatsWhitespace(c, flats)

        # add regex flattened token
        lf = LicenseFlat()
        lf.type = FlatType.REGEX
        lf.lineno = c.lineno
        lf.regex = regex
        flats.append(lf)

        # add spacing after if applicable
        if spacing in [NodeSpacing.AFTER, NodeSpacing.BOTH]:
            self._addFlatsWhitespace(c, flats)

    def _addFlatsOptional(self, c, flats, spacing):
        # add spacing before if applicable
        # FIXME decide whether to treat UNSPECIFIED as equivalent to BEFORE
        if spacing in [NodeSpacing.BEFORE, NodeSpacing.BOTH, NodeSpacing.UNSPECIFIED]:
            self._addFlatsWhitespace(c, flats)

        # add optional flattened token
        lf = LicenseFlat()
        lf.type = FlatType.OPTIONAL
        lf.lineno = c.lineno
        lf.children = []
        # add flattened tokens _to this flat token, not overall_,
        # for the optional node's own children
        self._flattenChildren(c, lf.children)
        flats.append(lf)

        # add spacing after if applicable
        if spacing in [NodeSpacing.AFTER, NodeSpacing.BOTH]:
            self._addFlatsWhitespace(c, flats)
