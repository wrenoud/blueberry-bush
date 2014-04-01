import unittest
import pickle
import tempfile
import os
from time import time

from FileState import FileState, FileStateLocal

class FileStateLocal_Tests(unittest.TestCase):
    def mkfile(self, contents):
        with open(self.path,'w') as f:
            f.write(contents)
        os.utime(self.path, (time(), self.modified))

    def rmfile(self):
        os.remove(self.path)
        
    def setUp(self):
        f, self.path = tempfile.mkstemp()
        os.close(f)
        self.modified = time() - 10
        self.mkfile("Hello World")
        self.filestate = FileStateLocal(os.path.dirname(self.path), self.path)
        
    def tearDown(self):
        self.rmfile()
        
    def test_key(self):
        self.assertEqual(self.filestate.key, os.path.basename(self.path))

    def test_local_path(self):
        self.assertEqual(self.filestate.local_path, self.path)

    def test_pickle(self):
        pickled = pickle.loads(pickle.dumps(self.filestate))
        self.assertEqual(self.filestate, pickled)

    def test_exists(self):
        self.rmfile()
        self.assertFalse(self.filestate.check_exists())
        self.assertEqual(self.filestate.state, FileState.STATE_DELETED)
        self.mkfile("Hello World")
        self.assertTrue(self.filestate.check_exists())

    def test_modified(self):
        self.assertFalse(self.filestate.check_modified()) # time should be unset
        self.assertEqual(self.filestate.modified, self.modified)
        self.assertEqual(self.filestate.state, FileState.STATE_MODIFIED)
        #should be unchanged now
        self.assertTrue(self.filestate.check_modified())

    def test_size(self):
        self.assertFalse(self.filestate.check_size()) # size should be unset
        self.assertEqual(self.filestate.size, 11)
        self.assertEqual(self.filestate.state, FileState.STATE_MODIFIED)
        #should be unchanged now
        self.assertTrue(self.filestate.check_size())
    
    def test_hash(self):
        self.assertFalse(self.filestate.check_hash()) # hash should be unset
        self.assertEqual(self.filestate.hash, 'b10a8db164e0754105b7a99be72e3fe5')
        self.assertEqual(self.filestate.state, FileState.STATE_MODIFIED)
        #should be unchanged now
        self.assertTrue(self.filestate.check_hash())

def main():
    unittest.main()

if __name__ == '__main__':
    main()