
from __future__ import with_statement
import HTMLParser
from contextlib import closing

class HtmlReader(HTMLParser.HTMLParser):
    
    def __init__(self, handler):
        HTMLParser.HTMLParser.__init__(self)
        #self._encoding = 'ISO-8859-1'
        self._handler = handler
    
    def parseFile(self, path):
        with closing(open(path, 'r')) as links:
            for l in links:
                self.feed(l)
        
        self.close()

    def handle_starttag(self, tag, attrs):
        param = {}
        for k, v in attrs:
            param[str(k)] = v
            
        if hasattr(self._handler, tag+'_start'):   
            getattr(self._handler, tag+'_start')(**param)

    def handle_endtag(self, tag):
        if hasattr(self._handler, tag+'_end'):
            getattr(self._handler, tag+'_end')()

