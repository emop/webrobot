
import re
from sailing.common.utils import PathUtils as utils

links = re.compile(r'((href|src|background)=(\'[^\']*\'|"[^"]*"|[^\s>]*))', re.I)
import logging

class LinkCrawler(object):
    
    def __init__(self, ):
        pass
        self.logger = logging.getLogger("linkCrawler")
    
    def crawling(self, path, url, action=None):
        fd = open(path, "r")
        data = fd.read()
        fd.close()
        
        data = self._crawling_data(data, url, action)
        
        fd = open(path, "w")
        fd.write(data)
        fd.close()
        
    def _crawling_data(self, data, url, action=None):
        
        if action is None: action = lambda x:x
        
        def repl(m):
            l = m.group(3).strip("'").strip('"')
            #print "url:%s" % url
            local_path = action(l)
            if local_path:
                local_url = utils.relative_url(url, local_path)
            else:
                local_url = l
            #print "local_url:%s" % local_url
            
            #self.logger.info("%s-->%s" % (l, local_url))
            return "%s='%s'" % (m.group(2), local_url)
        
        return re.sub(links, repl, data)
        
        
if __name__ == "__main__":
    link = LinkCrawler()
    
    testing = """"
<a href=123.html>test</a>

<img href="/abc.jpg">test</img>
href="/Article/zhihui/20090526014217.htm"
    """
    print link._crawling_data(testing, "/abc")
