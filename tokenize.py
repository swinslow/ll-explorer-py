# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

import re

from datatypes import License, LicenseFlat, FlatType, TargetText

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

class TextTokenizerConfig:
    def __init__(self):
        super(TextTokenizerConfig, self).__init__()

        # should multiple adjacent hyphen-like objects be combined
        # into a single hyphen?
        self.combineHyphens = True

class TextTokenizer:
    def __init__(self, cfg):
        super(TextTokenizer, self).__init__()

        # tokenizer configuration object
        self.cfg = cfg

    # Converts a text string into a list of transformed and cleaned
    # tokens, implementing portions of the SPDX Matching Guidelines.
    # given:  tt: datatypes.TargetText
    # result: stores the tokenized list in tt.tokens
    def tokenize(self, tt):
        tokens = []
        r = re.compile(r"(\S+)")
