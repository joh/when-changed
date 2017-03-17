#! /usr/bin/env python

import unittest
from whenchanged import whenchanged

class TestParseArgs(unittest.TestCase):
    def test_simple(self):
        wc = whenchanged.parse_args('when-changed /dev/null true'.split(' '))
        self.assertIsNotNone(wc)

        self.assertFalse(wc.recursive)
        self.assertFalse(wc.run_once)
        self.assertFalse(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_help(self):
        wc = whenchanged.parse_args('when-changed -h'.split(' '))
        self.assertIsNone(wc)

    def test_long_command(self):
        wc = whenchanged.parse_args('when-changed /dev/null echo changed'.split(' '))
        self.assertIsNotNone(wc)

        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_all_options_attached(self):
        wc = whenchanged.parse_args('when-changed -sr1v /dev/null true'.split(' '))
        self.assertIsNotNone(wc)

        self.assertTrue(wc.recursive)
        self.assertTrue(wc.run_once)
        self.assertTrue(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_all_options(self):
        wc = whenchanged.parse_args('when-changed -s -r -1 -v /dev/null true'.split(' '))
        self.assertIsNotNone(wc)

        self.assertTrue(wc.recursive)
        self.assertTrue(wc.run_once)
        self.assertTrue(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_command_c(self):
        wc = whenchanged.parse_args('when-changed /dev/null /dev -c echo changed'.split(' '))
        self.assertIsNotNone(wc)

        self.assertEqual(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_command_c_and_options(self):
        wc = whenchanged.parse_args('when-changed -r /dev/null /dev -c echo changed'.split(' '))
        self.assertIsNotNone(wc)

        self.assertTrue(wc.recursive)
        self.assertEqual(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_command_cattached(self):
        wc = whenchanged.parse_args('when-changed /dev/null /dev -ctrue'.split(' '))
        self.assertIsNotNone(wc)

        self.assertEqual(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['true'])

if __name__ == "__main__":
    unittest.main()
