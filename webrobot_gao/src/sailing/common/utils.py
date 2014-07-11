from common import *
import re

def import_class(cls ):
    
    try:
        mods = cls.split(".")
        mod = ".".join(mods[:-1])
        cls = mods[-1]
        
        mod = __import__(mod, globals(), locals(), ['', ], -1)        
        return getattr(mod, cls)
    except:
        raise
    
    return None

class PathUtils(object):
    
    @staticmethod
    def absolute_path(path1, path2):        
        if not path2: return path2
        dir = dir_name(path2)
        name = PathUtils.formats_name(base_name(path2))
        if path2[0] == '/':
            return join_path(dir, name)[1:]
        
        return norm_path(join_path(dir_name(path1), dir, name))

    @staticmethod
    def absolute_url(url1, url2):
        if not url2: return url2
        if url2[0] == "/": return url2
        url = norm_path(join_path(dir_name(url1), url2))
        return re.sub(r"[/\\]", "/", url)
        
    @staticmethod
    def relative_url(path1, path2):
        if not path2: return path2
        dir1 = re.split(r"\\|/", dir_name(path1))
        dir1 = [ e for e in dir1 if e ]
        dir2 = re.split(r"\\|/", dir_name(path2))
        dir2 = [ e for e in dir2 if e ]
        
        dir1.reverse()
        dir2.reverse()
        while dir1 and dir2 and dir1[-1] == dir2[-1]:
            dir1.pop()
            dir2.pop()
            
        dir2.extend(['..'] * len(dir1))
        dir2.reverse()
        dir2.append(base_name(path2))
        return "/".join(dir2)
        
    @staticmethod
    def formats_name(name):
        n, ext = os.path.splitext(name)
        if ext.lower() in ['.js', '.gif', '.jpg', '.jpeg', '.htm', 
                           '.html', '.zip', '.css', '.mp3']:
            return name
        
        name = re.sub(r"[?=&.]", "_", name) or 'index'
        return "%s.html" % name
        
#print PathUtils.relative_url("a.html", "/a/c/b.html")
        