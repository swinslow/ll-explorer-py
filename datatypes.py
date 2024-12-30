# SPDX-License-Identifier: MIT
# Copyright 2024 Steve Winslow

from enum import Enum

# Represents a parsed SPDX License List XML file.
class License:
    def __init__(self):
        super(License, self).__init__()

        # license ID
        self.id = ""

        # license name
        self.name = ""

        # whether or not OSI-approved
        self.osi = False

        # which version of the license list it was added in
        self.versionAdded = ""

        # which version of the license list it was deprecated in;
        # empty string if not deprecated
        self.versionDeprecated = ""

        # list of cross-reference URLs
        self.crossRefs = []

        # content of any notes
        self.notes = ""

        # original unparsed XML text for full license
        self.origXML = ""

        # top-level processed text node - LicenseNode
        self.textNode = None

# Enum for different types of parsed license nodes.
class NodeType(Enum):
    INVALID     = 0
    TOPTEXT     = 1     # top-level <text> node
    P           = 2
    TITLE       = 3
    COPYRIGHT   = 4
    LIST        = 5
    ITEM        = 6
    BULLET      = 7
    BR          = 8
    OPTIONAL    = 9
    ALT         = 10
    SLHEADER    = 11    # standard license header
    WHITESPACE  = 98    # a created node representing whitespace only
    PLAINTEXT   = 99    # a created node representing plain text

# Enum for spacing values for applicable license nodes.
class NodeSpacing(Enum):
    INVALID     = 0
    NONE        = 1
    BEFORE      = 2
    AFTER       = 3
    BOTH        = 4
    UNSPECIFIED = 99

# Represents a single parsed / processed node.
class LicenseNode:
    def __init__(self):
        super(LicenseNode, self).__init__()

        # node type
        self.type = NodeType.INVALID

        # this node's parent (or None for top-level TOPTEXT node)
        self.parent = None

        # starting coords for this element within XML file
        self.lineno = 0
        # FIXME lxml doesn't currently appear to provide column numbers
        # self.column = 0

        # list of child nodes
        self.children = []

        # spacing (for optional and alt items)
        # FIXME schema says default is 'before' if not stated, but in practice
        # FIXME I don't know if this is correct
        self.spacing = NodeSpacing.INVALID

        # matching regex (for alt items)
        self.regex = ""

        # matching name (for alt items)
        self.matchName = ""

        # text content for this node (for PLAINTEXT nodes only)
        self.text = ""
