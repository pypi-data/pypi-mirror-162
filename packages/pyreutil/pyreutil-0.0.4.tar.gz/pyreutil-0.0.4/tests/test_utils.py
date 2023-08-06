import unittest

from pyreutil.utils import *

class TestUtils(unittest.TestCase):
    
    def test_get_subdir_and_file_from_dir(self):
        original_dir = 'home/user/dir1'
        fullpath = 'home/user/dir1/dir2/dir3/file.txt'
        subdirs, filename = get_subdir_and_file_from_dir(fullpath, original_dir)
        self.assertEqual(subdirs, ['dir2', 'dir3'])
        self.assertEqual(filename, 'file.txt')