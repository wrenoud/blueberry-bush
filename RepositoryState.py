import os
from FileState import FileStateLocal

class Remote(object):

    def __init__(self): pass
    
    def create(self): pass
    def update(self): pass
    def modified(self): pass
    def delete(self): pass

class RepositoryState(object):
    """Manages the sync information, this includes the local root, ingnores, files, and update que"""
    def __init__(self, rootpath):
        self.root = os.path.abspath(rootpath)
        self.local_files = {}

    def create(self, src_path):
        local_file = FileStateLocal(self.root, src_path)
        if local_file.check_exists():
            local_file.check_modified()
            local_file.check_size()
            local_file.check_hash()
            self.local_files[local_file.key] = local_file
            
            return local_file.key

    def modified(self, src_path):
        src_key = FileStateLocal.as_key(self.root,src_path)
        self.local_files[src_key].check_size()
        self.local_files[src_key].check_modified()
        self.local_files[src_key].check_hash()
        
        return src_key
        
    def move(self, src_path, dest_path):
        src_key = FileStateLocal.as_key(self.root,src_path)
        self.local_files[src_key].local_path = dest_path
        dest_key = self.local_files[src_key].key
        self.local_files[dest_key] = self.local_files.pop(src_key)
        
        return (src_key,dest_key)

    def delete(self, src_path):
        src_key = FileStateLocal.as_key(self.root,src_path)
        del self.local_files[src_key]
        
        return src_key
        
    def ignore(self, src_path):
        dir, name = os.path.split(src_path)
        if name.startswith(".~lock"): return True
        if name.endswith("~"): return True
        if name == STATE_FILE: return True
        return False

