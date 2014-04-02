import unittest
import pickle
import tempfile
import os
import sys
from time import time

from FileState import FileState, FileStateLocal
from RepositoryState import RepositoryState

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


class RepositoryState_Tests(unittest.TestCase):
    def newTempFile(self, contents):
        f, path = tempfile.mkstemp()
        self.paths.append(path)
        os.write(f,contents)
        os.close(f)
        os.utime(path, (time(), self.modified))
        return path

    def setUp(self):
        self.paths = []
        self.modified = time() - 10
        self.newTempFile("1")
        self.repo = RepositoryState(os.path.dirname(self.paths[0]))
        self.repo.create(self.paths[0])

    def tearDown(self):
        for path in self.paths:
            os.remove(path)
            
    def test_create(self):
        key = self.repo.create(self.newTempFile("Hello World"))
        self.assertEqual(key, os.path.basename(self.paths[-1])) # check return value
        # check that everything updated
        self.assertEqual(self.repo.local_files[key].modified, self.modified) 
        self.assertEqual(self.repo.local_files[key].size, 11)
        self.assertEqual(self.repo.local_files[key].hash, 'b10a8db164e0754105b7a99be72e3fe5')
        self.assertEqual(len(self.repo.local_files), 2)
        
    def test_modified(self):
        with open(self.paths[-1],'w') as f: f.write("New World")
        os.utime(self.paths[-1], (time(), self.modified + 1))
        key = self.repo.modified(self.paths[-1])
        self.assertEqual(key, os.path.basename(self.paths[-1])) # check return value
        # check that everything updated
        self.assertEqual(self.repo.local_files[key].modified, self.modified + 1)
        self.assertEqual(self.repo.local_files[key].size, 9)
        self.assertEqual(self.repo.local_files[key].hash, '6b9b6d4c6631de42fcd8a82cd1b5816b')

    def test_move(self):
        src_path = self.paths[0]
        src_key, dst_key = self.repo.move(src_path, src_path + "asdf")
        self.assertEqual(src_key, dst_key[:-4]) # check return value
        self.assertEqual(dst_key, os.path.basename(src_path + "asdf"))
        
    def test_delete(self):
        key = self.repo.delete(self.paths[-1])
        self.assertEqual(key, os.path.basename(self.paths[-1])) # check return value
        self.assertEqual(len(self.repo.local_files), 0)
        
def main():
    unittest.main()

if __name__ == '__main__':
    main()