import os
import hashlib

class FileState(object):
    STATE_NORMAL = 0x00
    STATE_MODIFIED = 0x01
    STATE_DELETED = 0x03
    # STATE_MOVED = 0x04
    STATE_NEW = 0x05
   
    """Holds state information for a file"""
    __slots__ = ('state','key','modified','hash','size')
        
    def __init__(self, key='', modified=0, hash=None, size=0):
        self.state = self.STATE_NORMAL
        self.key = key
        self.modified = modified
        self.hash = hash
        self.size = size

    def clear_state(self):
        self.state = self.STATE_NORMAL
        
    def check_exists(self): pass
    def check_modified(self): pass
    def check_size(self): pass
    def check_hash(self): pass

    def __setstate__(self, state):
        self.state, self.key, self.modified, self.hash, self.size = state

    def __getstate__(self):
        return (self.state, self.key, self.modified, self.hash, self.size)

    def __eq__(self,cmp):
        return self.state == cmp.state and \
                self.key == cmp.key and \
                self.modified == cmp.modified and \
                self.hash == cmp.hash and \
                self.size == cmp.size


class FileStateLocal(FileState):
    __slots__ = ('local_dir','dropped')

    @staticmethod
    def as_key(local_dir, filepath):
        _clean = os.path.abspath(filepath) # make sure we have the real path
        key = os.path.relpath(_clean, local_dir)
        
        return key
        
    def __init__(self, local_dir, filepath):
        super(FileStateLocal, self).__init__()
        self.local_dir = local_dir
        self.local_path = filepath
        self.dropped = False
        
    @property
    def local_path(self):
        return os.path.join(self.local_dir, self.key)
    
    @local_path.setter
    def local_path(self,filepath):
        self.key = FileStateLocal.as_key(self.local_dir, filepath)
        
    def check_exists(self):
        if not os.path.exists(self.local_path):
            self.state = self.STATE_DELETED
            return False
        else:
            return True
        
    def check_modified(self):
        _mt = round(os.path.getmtime(self.local_path), 3) # only to the nearest millisecond
        if self.modified != _mt:
            self.state = self.STATE_MODIFIED
            self.modified = _mt
            return False
        else:
            return True

    def check_size(self):
        _sz = os.path.getsize(self.local_path)
        if self.size != _sz:
            self.state = self.STATE_MODIFIED
            self.size = _sz
            return False
        else:
            return True

    def check_hash(self, block_size=2**20):
        md5 = hashlib.md5()
        hash = None
        with open(self.local_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                md5.update(data)
        hash = md5.hexdigest()
        if self.hash != hash:
            self.state = self.STATE_MODIFIED
            self.hash = hash
            return False
        else:
            return True
        
        
    def __setstate__(self, state):
        _superstate, self.local_dir, self.dropped = state
        super(FileStateLocal, self).__setstate__(_superstate)

    def __getstate__(self):
        return (super(FileStateLocal, self).__getstate__(), self.local_dir, self.dropped)
        
    def __eq__(self,cmp):
        return super(FileStateLocal, self).__eq__(cmp) and \
                self.local_dir == cmp.local_dir and \
                self.dropped == cmp.dropped