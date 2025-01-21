# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

import re

from datatypes import License, LicenseFlat, FlatType, TargetText

# FIXME also handle trailing comment indicators: `**/`, `*/`, etc.

# FIXME consider whether this breaks any licenses with text that has
# FIXME lines beginning with comment characters, particularly `/`

# note we are using the Python \s regex values _except for_ \n,
# because we don't want the matching for spacing to capture the line break
_step2Regex = re.compile(r"(^|\n)([ \t\r\f\v]*)([/*#;%]+)([ \t\r\f\v]*)")

class LicenseTokenizerConfig:
    def __init__(self):
        super(LicenseTokenizerConfig, self).__init__()

        # should multiple adjacent hyphen-like objects be combined
        # into a single hyphen?
        self.combineHyphens = True

        # should adjacent flat whitespace nodes at the same level (e.g.,
        # not counting those under children of optional nodes) be
        # collapsed into a single whitespace node?
        self.mergeWhitespace = True

        # should leading / trailing whitespace in flattened text nodes
        # be converted to separate whitespace nodes?
        self.replaceTextWhitespace = True

        # regardless of replaceTextWhitespace, should we _remove_ whitespace
        # nodes if the preceding or subsequent node is an optional or
        # regex flat node with a spacing value that indicates no spacing?
        # FIXME to implement this, will need to carry spacing value into
        # FIXME LicenseFlat data
        self.removeConflictingWhitespace = True

class LicenseTokenizer:
    def __init__(self, cfg):
        super(LicenseTokenizer, self).__init__()

        # tokenizer configuration object
        self.cfg = cfg

    # Converts a License's flattened XML content into a list of
    # transformed and cleaned tokens, implementing portions of the
    # SPDX Matching Guidelines.
    # given:  lic: datatypes.License
    # result: stores the tokenized list in lic.tokens
    # throws: FIXME something if lic is not yet flattened
    def tokenize(self, lic):
        # FIXME throw something if lic is not yet flattened
        lic.tokens = self._tokenizeHelper(lic.textFlat)

    def _tokenizeHelper(self, fts):
        tokens = []
        for ft in fts:
            match ft.type:
                case FlatType.WHITESPACE:
                    self._tokenizeWhitespace(tokens, ft)
                case FlatType.TEXT:
                    self._tokenizeText(tokens, ft)
                case FlatType.OPTIONAL:
                    self._tokenizeOptional(tokens, ft)
                case FlatType.REGEX:
                    self._tokenizeRegex(tokens, ft)
                case _:
                    # FIXME handle invalid flat type
                    raise ValueError(f"Invalid flattened node {ft}")
        return tokens

    def _tokenizeWhitespace(self, tokens, ft):
        # if configured, check for duplicate whitespace preceding this one
        if (self.cfg.mergeWhitespace and len(l) > 0 and
            l[-1][0] == FlatType.WHITESPACE):
            return
        tokens.append((FlatType.WHITESPACE, ft, 0, None))

    def _tokenizeOptional(self, tokens, ft):
        # FIXME determine whether to do anything with
        # FIXME cfg.removeConflictingWhitespace here
        children = self._tokenizeHelper(ft.children)
        tokens.append((FlatType.OPTIONAL, ft, 0, children))

    def _tokenizeLicenseRegex(self, tokens, ft):
        # FIXME determine whether to do anything with
        # FIXME cfg.removeConflictingWhitespace here
        tokens.append((FlatType.REGEX, ft, 0, ft.regex))

    def _tokenizeText(self, tokens, ft):
        # FIXME IMPLEMENT
        pass

class TextPreprocessorConfig:
    def __init__(self):
        super(TextPreprocessorConfig, self).__init__()

        # should multiple adjacent hyphen-like objects be combined
        # into a single hyphen?
        self.combineHyphens = True

class TextPreprocessor:
    def __init__(self, cfg):
        super(TextPreprocessor, self).__init__()

        # preprocessor configuration object
        self.cfg = cfg

        # see docs/notes.md for descriptions of the following elements

        # original unmodified string being tested for matches
        self.orig = ""

        # mapping from original string to row/col values
        # list of tuples [(r1, c1), (r2, c2), ...] corresponding to
        # row/col values of each character in self.orig
        self.origrc = []

        # processed and converted string, ready for matching
        self.proc = ""

        # mapping from proc string to orig string
        # list of indices corresponding to iself.orig index of each
        # character in self.proc
        self.procmap = []

    # Converts a text string into a list of transformed and cleaned
    # characters, implementing portions of the SPDX Matching Guidelines,
    # with mappings to original string's corresponding characters.
    # given:  target: text string to process
    # result: Preprocessor is completed and values filled in
    def process(self, target):
        pass

    # Step 1: prepare row and col values
    def _step1(self):
        self.origrc = []
        r = 1
        c = 0
        for i in self.orig:
            c += 1
            self.origrc.append((r, c))
            if i == "\n":
                r += 1
                c = 0

    # Step 2: replace leading comment characters with spaces
    def _step2(self):
        self.proc = re.sub(_step2Regex,
            lambda m: m.group(1) + m.group(2) + " "*len(m.group(3)) + m.group(4),
            self.orig)
        self.procmap = list(range(len(self.proc)))

    # Step 3: convert to lowercase, adjusting character locations as needed
    def _step3(self):
        newProcList = []
        newProcMap = []
        origIdx = 0

        for c in list(self.proc):
            lo = c.lower()
            newProcList.append(lo)

            # if result is 1 character, just add current origIdx to procmap.
            # if result is >1, need to adjust origIdx accordingly.
            # note that this assumes that Step 3 is the first step to change
            # procmap from anything other than a 1:1 mapping.
            for _ in range(len(lo)):
                newProcMap.append(origIdx)
            origIdx += 1

        self.proc = "".join(newProcList)
        self.procmap = newProcMap
