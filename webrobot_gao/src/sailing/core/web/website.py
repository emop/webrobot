
from sailing.common.common import join_path

class WebSite(object):
    
    def __init__(self, hostname, local_path='', work_root='', meta={}):
        self.hostname = hostname or 'unknown.site'
        self.local_path = local_path or hostname
        self.work_root = work_root
    
    def real_path(self, url):
        
        if self.work_root:
            path = join_path(self.work_root, self.local_path, url)
        else:
            path = join_path(self.local_path, url)
            
        return path.replace(":", "_")
    
    