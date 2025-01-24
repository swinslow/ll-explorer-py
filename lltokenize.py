# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

import re

from datatypes import License, LicenseFlat, FlatType, TargetText

##### LICENSE XML TEXT TOKENIZING #####

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

##### REGEXES FOR MATCHING GUIDELINES PROCESSING #####

EQUIVALENTWORDS_PATH = "resources/equivalentwords.txt"

class TextPreprocessorRegexes:
    def __init__(self, equivalentsPath):
        super(TextPreprocessorRegexes, self).__init__()

        # Step 2: Remove leading comments
        # FIXME decide handling trailing comment indicators: `**/`, `*/`, etc.
        # FIXME consider whether this breaks any licenses with text that has
        # FIXME lines beginning with comment characters, particularly `/`
        # note we are using the Python \s regex values _except for_ \n,
        # because we don't want the matching for spacing to capture the line break
        self._step2Regex = re.compile(r"(^|\n)([ \t\r\f\v]*)([/*#;%]+)([ \t\r\f\v]*)")

        # Step 4(a): Remove separators on own lines with optional whitespace
        #_step4aRegex = re.compile(r"(^|\n)([ \t\r\f\v]*)[^a-zA-Z0-9\s]\1{2,}([ \t\r\f\v]*)")
        self._step4aRegex = re.compile(r"(^|\n)([ \t\r\f\v]*)([^a-zA-Z0-9\s])\3{2,}([ \t\r\f\v]*)")

        # Step 4(b): Convert whitespace
        self._step4bRegex = re.compile(r"\s+")

        # Step 4(c): Convert hyphen-like characters
        # FIXME there are a lot of them, consider which others to include
        self._step4cRegex = re.compile(r"[-‐‑‒–—―]+")

        # Step 4(d): Convert quote-like characters
        # FIXME there are a lot of them, consider which others to include
        self._step4dRegex = re.compile(r"['\"«»‘’‚‛“”„‟‹›`]+")

        # Step 5(a): Convert copyright symbol
        self._step5aRegex = re.compile(r"©")

        # Step 5(b): Convert http protocol
        self._step5bRegex = re.compile(r"http\:\/\/")

        # Step 5(c): Convert equivalent words
        # list of tuples in form [(to, from, regexFrom), ...]
        self._equivalents = []
        with open(equivalentsPath, "r") as f:
            lines = f.readlines()
        for line in lines:
            res = line.strip().split(",")
            self._equivalents.append((
                res[0],
                res[1],
                re.compile(r"(^|[^a-zA-Z])(" + res[1] + r")($|[^a-zA-Z])")
            ))

##### TEXT PREPROCESSING #####

class TextPreprocessorConfig:
    def __init__(self):
        super(TextPreprocessorConfig, self).__init__()

        # should multiple adjacent hyphen-like objects be combined
        # into a single hyphen?
        self.combineHyphens = True

        # regexes for preprocessor
        self.regexes = TextPreprocessorRegexes(EQUIVALENTWORDS_PATH)

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
        self.orig = target
        self._step1()
        self._step2()
        self._step3()
        self._step4a()
        self._step4b()
        self._step4c()
        self._step4d()
        self._step5a()
        self._step5b()
        self._step5c()

    ##### PROCESSING STEP FUNCTIONS #####

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
        self.proc = re.sub(self.cfg.regexes._step2Regex,
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

    # Step 4(a): remove separators (>3 adjacent non-alphanumeric characters)
    def _step4a(self):
        self._helperReplaceAll(
            self.cfg.regexes._step4aRegex,
            lambda m: m.group(1) + m.group(2) + m.group(4)
        )

    # Step 4(b): convert whitespace
    def _step4b(self):
        self._helperReplaceAll(self.cfg.regexes._step4bRegex, lambda _: " ")

    # Step 4(c): convert hyphen-like characters
    def _step4c(self):
        self._helperReplaceAll(
            self.cfg.regexes._step4cRegex,
            lambda m: "-" if self.cfg.combineHyphens else "-"*(len(m.group(0)))
        )

    # Step 4(d): convert quote-like characters
    def _step4d(self):
        self._helperReplaceAll(self.cfg.regexes._step4dRegex, lambda _: "'")

    # Step 5(a): convert copyright symbol
    def _step5a(self):
        self._helperReplaceAll(self.cfg.regexes._step5aRegex, lambda _: "(c)")

    # Step 5(b): convert http protocol
    def _step5b(self):
        self._helperReplaceAll(self.cfg.regexes._step5bRegex, lambda _: "https://")

    # Step 5(c): convert equivalent words
    def _step5c(self):
        for equivTuple in self.cfg.regexes._equivalents:
            self._helperReplaceAll(
                equivTuple[2],
                lambda m: m.group(1) + equivTuple[0] + m.group(3)
            )

    ##### HELPER FUNCTIONS #####

    # Helper function to replace portion of a string and adjust procmap.
    # given:  - startIdx: index of first character in self.proc to replace
    #         - numReplace: # of characters in self.proc to replace
    #         - newText: string to insert in place of removed characters
    # result: newText is inserted into self.proc in place of replaced chars;
    #         self.procmap is updated to preserve prior mappings
    # return: index of next _unreplaced_ character
    def _helperReplace(self, startIdx, numReplace, newText):
        # replace characters in self.proc
        self.proc = self.proc[:startIdx] + newText + self.proc[startIdx+numReplace:]

        # determine what we're doing to self.procmap based on difference
        # in length of old vs. replacement characters
        lt = len(newText)
        diff = lt - numReplace
        if diff < 0:
            # shorter string => remove excess characters
            repStart = startIdx + lt
            repEnd = repStart - diff
            self.procmap[repStart:repEnd] = []
        elif diff > 0:
            # longer string => add repeats of last extended value
            ext = startIdx + numReplace
            rep = [self.procmap[ext - 1]] * diff
            self.procmap = self.procmap[:ext] + rep + self.procmap[ext:]
        # no change to procmap if diff == 0

        # return index of next unreplaced character
        return startIdx + lt

    # Helper function to replace all portions of a string matching a regex and
    # adjust procmap.
    # given:  - r: raw-string regex to match against
    #         - l: function taking an re.Match object and returning string
    #              to replace matched portion
    # result: all instances of matching strings are replaced with corresponding
    #         calls to l(m); self.procmap is updated
    def _helperReplaceAll(self, r, l):
        idx = 0
        while True:
            m = re.search(r, self.proc[idx:])
            if m is None:
                break
            idx = self._helperReplace(m.start() + idx, m.end()-m.start(), l(m))
