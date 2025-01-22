# SPDX-License-Identifier: MIT
# Copyright 2025 Steve Winslow

import unittest

from lltokenize import TextPreprocessorConfig, TextPreprocessor

class TextPreprocessorTestSuite(unittest.TestCase):
    def setUp(self):
        cfg = TextPreprocessorConfig()
        self.tp = TextPreprocessor(cfg)

    def tearDown(self):
        pass

    ##### SMOKE TEST #####

    def test_smoke_initial_values(self):
        self.assertIsNotNone(self.tp)
        self.assertIsNotNone(self.tp.cfg)
        self.assertTrue(self.tp.cfg.combineHyphens)
        self.assertEqual(self.tp.orig, "")
        self.assertEqual(self.tp.origrc, [])
        self.assertEqual(self.tp.proc, "")
        self.assertEqual(self.tp.procmap, [])

    ##### PRIMARY STEP TESTS #####

    def test_step1(self):
        # testing creation of initial chars mapping index
        self.tp.orig = "Line 1\nline 2"
        self.tp._step1()

        # origrc should have same number of elements as string length
        self.assertEqual(len(self.tp.origrc), 13)

        # test a few characters' values
        # first "n" - rows and cols are 1-indexed
        self.assertEqual(self.tp.origrc[2], (1, 3))
        # first newline
        self.assertEqual(self.tp.origrc[6], (1, 7))
        # "l" at start of "line 2" => next line
        self.assertEqual(self.tp.origrc[7], (2, 1))
        # last character - should be "2", not newline
        self.assertEqual(self.tp.origrc[-1], (2, 6))
        self.assertEqual(self.tp.orig[-1], "2")

    def test_step2_basic_removal(self):
        # testing removal of # comment chars at beginning of lines
        t    = """# Commented out
 Not commented out
Don't drop at end #
# Later comment
Don't drop at end #"""

        want = """  Commented out
 Not commented out
Don't drop at end #
  Later comment
Don't drop at end #"""

        self.tp.orig = t
        self.tp._step1()
        self.tp._step2()

        # comment chars (#) at _start_ of lines should be removed,
        # but not at end of lines
        self.assertEqual(self.tp.proc, want)

        # length of proc should be unchanged
        self.assertEqual(len(self.tp.proc), len(self.tp.orig))

        # orig should be unchanged
        self.assertEqual(self.tp.orig, t)

        # confirm procmap has been set with no adjustments
        self.assertEqual(self.tp.procmap[0], 0)
        self.assertEqual(self.tp.procmap[45], 45)
        self.assertEqual(self.tp.procmap[89], 89)

    def test_step3_normal_lowercase(self):
        # testing lowercasing of all letters, where no change in length occurs
        t    = "Hello World!"
        want = "hello world!"

        self.tp.orig = t
        self.tp._step1()
        self.tp._step2()

        # save procmap before final step, for testing
        procmapBefore = list(self.tp.procmap)
        self.tp._step3()

        # proc should now be all lowercase
        self.assertEqual(self.tp.proc, want)

        # procmap entries should not have changed (for this lowercasing)
        self.assertEqual(self.tp.procmap, procmapBefore)

    def test_step3_expanded_lowercase(self):
        # testing lowercasing where Unicode character results in _longer_ string
        t    = "aİsd"
        want = "ai̇sd"
        wantProcmap = [0, 1, 1, 2, 3]

        self.tp.orig = t
        self.tp._step1()
        self.tp._step2()
        self.tp._step3()

        # proc should now be all lowercase, with expanded length
        self.assertEqual(len(self.tp.proc), 5)
        self.assertEqual(self.tp.proc, want)

        # procmap should be expanded as well
        self.assertEqual(self.tp.procmap, wantProcmap)

    ##### HELPER TESTS #####

    def test_helper_replace_chars_same_length(self):
        t    = "hello world"
        want = "heABCDEFrld"
        wantProcmap = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        self.tp.orig = t
        self.tp.proc = self.tp.orig
        self.tp.procmap = list(range(len(self.tp.proc)))

        self.tp._helperReplace(2, 6, "ABCDEF")

        # proc should now contain replacement string, and be same length
        self.assertEqual(self.tp.proc, want)

        # procmap should not have changed
        self.assertEqual(self.tp.procmap, wantProcmap)

    def test_helper_replace_chars_longer(self):
        t    = "hello world"
        want = "heABCDEFGHIrld"
        wantProcmap = [0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8, 9, 10]

        self.tp.orig = t
        self.tp.proc = self.tp.orig
        self.tp.procmap = list(range(len(self.tp.proc)))

        self.tp._helperReplace(2, 6, "ABCDEFGHI")

        # proc should now contain replacement string, and be longer as a result
        self.assertEqual(self.tp.proc, want)

        # procmap should be expanded, with repeating last character for added ones
        self.assertEqual(self.tp.procmap, wantProcmap)

    def test_helper_replace_chars_shorter(self):
        t    = "hello world"
        want = "heABCrld"
        wantProcmap = [0, 1, 2, 3, 4, 8, 9, 10]

        self.tp.orig = t
        self.tp.proc = self.tp.orig
        self.tp.procmap = list(range(len(self.tp.proc)))

        self.tp._helperReplace(2, 6, "ABC")

        # proc should now contain replacement string, and be shorter as a result
        self.assertEqual(self.tp.proc, want)

        # procmap should be shortened, losing some values
        self.assertEqual(self.tp.procmap, wantProcmap)
