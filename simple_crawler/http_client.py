# -*- coding: gbk -*-

import urllib2, httplib
import StringIO
import gzip
from urlparse import urlparse
#from sailing.common.common import *
import logging

class HTTPClient(object):
    
    def __init__(self, www_root=None):
        self.proxy = None
        self.last_url = None
        self.logger = logging.getLogger("HttpClient")
        
        
        #import urllib
    
    def set_proxy(self, proxy, www_root=None):
        if proxy:
            self.proxy = urllib2.ProxyHandler(proxy)
            
    def _http_handlers(self):
        return self.proxy and [self.proxy, ] or []
    
    def download(self, url, headers={}):
        
        self.logger.info("download:%s" % (url, ))
        #url = self.relative_path(url)
        data = None
        try:
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip') 
            for k, v in headers.iteritems():
                request.add_header(k, v)
            opener = urllib2.build_opener(*self._http_handlers())            
            f = opener.open(request)
            encoding = f.headers.get('Content-Encoding')
            if encoding and 'gzip' in encoding:
                compresseddata = f.read()
                compressedstream = StringIO.StringIO(compresseddata)   
                gzipper = gzip.GzipFile(fileobj=compressedstream)      
                data = gzipper.read()
                gzipper.close()
            else:
                data = f.read()
                f.close()
        except urllib2.HTTPError, e:
            raise
        
        return data
    