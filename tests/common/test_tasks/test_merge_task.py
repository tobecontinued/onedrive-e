import unittest

from onedrived.common.tasks import merge_task


class TestMergeTaskHelperFunctions(unittest.TestCase):

    def test_unpack_first_item(self):
        d = {'key': 'val'}
        key, val = merge_task._unpack_first_item(d)
        self.assertEqual('key', key)
        self.assertEqual('val', val)
        self.assertEqual(1, len(d))


if __name__ == '__main__':
    unittest.main()
