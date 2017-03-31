#! /usr/bin/env python

import unittest
try:
    from whenchanged import whenchanged
except:
    import whenchanged

class TestParseArgs(unittest.TestCase):
    def assertSimilar(self, l1, l2):
        return self.assertEqual(sorted(l1), sorted(l2))

    def construct_WhenChanged(self, cmd):
        return whenchanged.WhenChanged(**whenchanged.parse_args(cmd.split(' ')))

    def test_simple(self):
        wc = self.construct_WhenChanged('when-changed /dev/null true')

        self.assertFalse(wc.recursive)
        self.assertFalse(wc.run_once)
        self.assertFalse(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_help(self):
        self.assertIsNone(whenchanged.parse_args('when-changed -h'.split(' ')))

    def test_long_command(self):
        wc = self.construct_WhenChanged('when-changed /dev/null echo changed')

        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_all_options_attached(self):
        wc = self.construct_WhenChanged('when-changed -sr1v /dev/null true')

        self.assertTrue(wc.recursive)
        self.assertTrue(wc.run_once)
        self.assertTrue(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_all_options(self):
        wc = self.construct_WhenChanged('when-changed -s -r -1 -v /dev/null true')

        self.assertTrue(wc.recursive)
        self.assertTrue(wc.run_once)
        self.assertTrue(wc.run_at_start)
        self.assertEqual(list(wc.paths), ['/dev/null'])
        self.assertEqual(wc.command, ['true'])

    def test_command_c(self):
        wc = self.construct_WhenChanged('when-changed /dev/null /dev -c echo changed')

        self.assertSimilar(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_command_c_followed_by_other(self):
        wc = self.construct_WhenChanged('when-changed /dev/null /dev -c ls -r')

        self.assertFalse(wc.recursive)
        self.assertSimilar(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['ls', '-r'])

    def test_command_c_and_options(self):
        wc = self.construct_WhenChanged('when-changed -r /dev/null /dev -c echo changed')

        self.assertTrue(wc.recursive)
        self.assertSimilar(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['echo', 'changed'])

    def test_command_cattached(self):
        wc = self.construct_WhenChanged('when-changed /dev/null /dev -ctrue')

        self.assertSimilar(list(wc.paths), ['/dev/null', '/dev'])
        self.assertEqual(wc.command, ['true'])

if __name__ == "__main__":
    unittest.main()
