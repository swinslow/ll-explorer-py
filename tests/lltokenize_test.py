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

    def test_smoke_initial_values(self):
        self.assertIsNotNone(self.tp)
        self.assertIsNotNone(self.tp.cfg)
        self.assertTrue(self.tp.cfg.combineHyphens)
        self.assertEqual(self.tp.orig, "")
        self.assertEqual(self.tp.origrc, [])
        self.assertEqual(self.tp.proc, "")
        self.assertEqual(self.tp.procmap, [])

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
