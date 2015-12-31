__author__ = 'xb'

import unittest

from onedrived.api import options


class TestNameConflictBehavior(unittest.TestCase):
    """
    The definition of nameConflictBehavior can be referred to at:
    https://github.com/OneDrive/onedrive-api-docs/blob/master/items/create.md
    """

    def test_default(self):
        self.assertIsNotNone(options.NameConflictBehavior.DEFAULT)
        self.assertIn(options.NameConflictBehavior.DEFAULT, ['rename', 'replace', 'fail'])

    def test_values(self):
        self.assertEqual('rename', options.NameConflictBehavior.RENAME)
        self.assertEqual('replace', options.NameConflictBehavior.REPLACE)
        self.assertEqual('fail', options.NameConflictBehavior.FAIL)


if __name__ == '__main__':
    unittest.main()
