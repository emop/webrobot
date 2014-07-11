from __future__ import with_statement
from contextlib import closing
from sailing.common.common import *
import codecs

def new_task(sailor='', status='new'):

    return FileTask(work_dir=sailor, status=status)


def id_generater():
    id = 0
    while True:
        id = id > 10000 and 0 or id + 1
        yield "%06d" % id

class FileTask(object):
    
    current_id = id_generater()
    
    def __init__(self, path=None, work_dir=None, status=None):
        
        if path:
            self._init_task(path)
        elif work_dir and status:
            self._create_task(work_dir, status)
        else:
            raise RuntimeError, "Invalid FileTask parameter!"
        
        self._writer = None
        self.headers = None
        self.cur_id = 0
        
    def _next_data_id(self):
        self.cur_id += 1
        return "%06d" % self.cur_id

    def _init_task(self, path, create=False):
        if not exists_path(path):
            if create is True:
                make_path(dir_name(path))
                open(path, 'w').close()
            else:
                raise RuntimeError, "Not found task '%s'" % path
            
        self._path = path
        self._id, self._status = os.path.splitext(path)
        self._status = self._status[1:]
    
    @property
    def path(self): return self._path
    
    def _create_task(self, work_dir, status='new'):
        
        task_id = self.current_id.next()
        exists_task = lambda x: len(glob.glob(join_path(work_dir, "%s.*" % x))) > 0

        while exists_task(task_id): task_id = self.current_id.next()
        
        self._init_task(join_path(work_dir, "%s.%s" % (task_id, status)), create=True)
    
    def header(self, name=None, value=None):
        if self.headers is None: self._loading_headers()
        
        if value is None and name:
            if self.headers.has_key(name): return self.headers[name]
        elif value and self._writer is None:
            self.headers[name] = value
        elif self._writer is not None:
            raise RuntimeError, "Can't setting header after added action!"
        else:
            return self.headers
        
        return None
    
    def _loading_headers(self):
        
        self.headers = {}
        
        fd = codecs.open(self.path, 'r', "utf-8")
        with closing(fd) as links:
            for l in links:
                #end of header
                if not l.strip() or l[0].islower(): break
                if l.startswith("#") or l.count(':') == 0: continue
                name, value = l.split(":", 1)
                self.headers[name.strip()] = value.strip()
        fd.close()
                 
    def list_actions(self):
        
        fd = codecs.open(self.path, 'r', "utf-8")
        with closing(fd) as links:
            for l in links:
                #comment or empty line
                if l.startswith("#") or not l.strip():continue
                #header
                if l[0].isupper():continue
                yield l
        fd.close()
    
    def add_action(self, desc):
        self._get_writer().write(desc)
        if not desc.endswith('\n'):
            self._get_writer().write('\n')
            
    def remove_empty(self):
        actions = self.list_actions()
        try:
            actions.next()
        except:
            remove_path(self.path)
            
    def remove(self):
        remove_path(self.path)            
    
    def _get_writer(self):
        if self._writer is None:
            self._writer = open(self._path, 'w')
            if self.headers and len(self.headers) > 0:
                for k, v in self.headers.iteritems():
                    self._writer.write("%s:%s\n" % (k, v))
                    self._writer.write("\n")
        
        return self._writer
        
    def save_data(self, data_id, data):
        if not data_id: data_id = self._next_data_id()
        path = os.path.join(self._id, "%s.data" % data_id)
        if not os.path.isdir(self._id): os.mkdir(self._id)
        fd = open(path, 'w')
        fd.write(data)
        fd.close()        
        return data_id
        
    def get_data(self, data_id):
        path = os.path.join(self._id, "%s.data" % data_id)
        data = ""
        if os.path.isfile(path):
            fd = open(path, 'r')
            data = fd.read()
            fd.close()
        return data
        
    @staticmethod
    def search(path, status='*', pattern='*', len=5):
        
        path_list = glob.glob(join_path(path, '%s.%s' % (pattern, status)))[:len]
        
        return [ FileTask(e) for e in path_list ]
    
    def status(self, new_st=None):

        if new_st is None: return self._status
        
        old_st = self._status
        if new_st != self._status:
            #close the file handle of writing action.
            self.close()
            
            self._status = new_st
            new_st = "%s.%s" % (self._id, self._status)
            move_to(self._path, new_st)
            self._path = new_st
        
        return old_st
    
    def close(self):
        if self._writer: self._writer.close()
        self._writer = None
    
    def __del__(self):
        self.close()
        
    def __str__(self):
        return self.path
    
    def __repr__(self):
        return self.path    
    
    status = property(status, status)
    
