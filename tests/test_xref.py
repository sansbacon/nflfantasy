# -*- coding: utf-8 -*-
# tests/test_xref.py
# tests for nfl.xref module

import logging
import sys
import unittest

import nflfantasy.xref as nx
from nflmisc.nflpg import getdb


class Xref_test(unittest.TestCase):

    def setUp(self):
        db = getdb('nfl')
        self.fb = nx.Fanball(db)
        self.f4f = nx.F4f(db)

    @unittest.skip
    def test_fanball_add_xref(self):
        pass

    def test_fanball_get_mfld(self):
        self.assertIsInstance(self.fb.get_mfld(), dict)
        self.assertIsInstance(self.fb.get_mfld('mfl'), dict)
        self.assertIsInstance(self.fb.get_mfld('fb'), dict)
        self.assertIsInstance(self.fb.get_mfld('RANDO'), dict)

    def test_fanball_get_players(self):
        self.assertIsInstance(self.fb.get_players(), list)

    def test_fanball_get_playersd(self):
        self.assertIsInstance(self.fb.get_playersd('name'), dict)
        self.assertIsInstance(self.fb.get_playersd('namepos'), dict)
        with self.assertRaises(ValueError):
            self.fb.get_playersd('ERR')

    @unittest.skip
    def test_fanball_match_mfl(self):
        l = [{'a': 1}, {'b': 2}]
        self.assertIsInstance(self.fb.match_mfl(l, 'id', 'name', 'pos'), list)

    def test_f4f_get_mfld(self):
        self.assertIsInstance(self.f4f.get_mfld(), dict)
        self.assertIsInstance(self.f4f.get_mfld('mfl'), dict)
        self.assertIsInstance(self.f4f.get_mfld('f4f'), dict)
        self.assertIsInstance(self.f4f.get_mfld('RANDO'), dict)

    def test_f4f_get_players(self):
        self.assertIsInstance(self.f4f.get_players(), list)

    def test_f4f_get_playersd(self):
        self.assertIsInstance(self.f4f.get_playersd('name'), dict)
        self.assertIsInstance(self.f4f.get_playersd('namepos'), dict)
        with self.assertRaises(ValueError):
            self.f4f.get_playersd('ERR')

    def test_pff_get_mfld(self):
        self.assertIsInstance(self.pff.get_mfld(), dict)
        self.assertIsInstance(self.pff.get_mfld('mfl'), dict)
        self.assertIsInstance(self.pff.get_mfld('pff'), dict)
        self.assertIsInstance(self.pff.get_mfld('RANDO'), dict)

    def test_f4f_get_players(self):
        self.assertIsInstance(self.pff.get_players(), list)

    def test_f4f_get_playersd(self):
        self.assertIsInstance(self.pff.get_playersd('name'), dict)
        self.assertIsInstance(self.pff.get_playersd('namepos'), dict)
        with self.assertRaises(ValueError):
            self.pff.get_playersd('ERR')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
