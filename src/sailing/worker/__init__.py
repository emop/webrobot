import re

from sailing.core import Sailor, new_task
from sailing.conf import settings
from sailing.core.web.website import WebSite
from urlparse import urlparse
from sailing.common.utils import import_class
import logging

class Analyse(Sailor):
    
    def __init__(self):
        self.url_mapping = []
        self.crawlers = {}
        self.logger = logging.getLogger("worker")
    
    def idle(self):
        
        task = new_task('spider')

        url = urlparse(settings.START_INDEX)
        host_name = url.hostname
        if url.port: host_name += ":%s" % url.port
             
        task.header('Site', host_name)

        url_path = url.path
        if(url_path.endswith("/") or not url_path.strip()):
            url_path = "%sindex.html" % url_path

        task.add_action("%s ==> %s" % (settings.START_INDEX, url_path.strip("/")))
        
        task.status = 'waiting'
        
        self.logger.info("created new task '%s'." % task.path)
    
    def ready(self):
        self.url_mapping = settings.CROWERS_MAPPING
        self.crawlers = settings.CRAWLER
        for k, v in self.crawlers.iteritems():
            self.crawlers[k] = self._init_crawler(*v)
        
        self.default_crawlers = ()
        for pattern, crawlers in self.url_mapping:
            if pattern == 'default':
                self.default_crawlers = crawlers
                break
        
        for pattern, crawlers in self.url_mapping:
            for c in crawlers:
                if not self.crawlers.has_key(c):
                    raise RuntimeError, "Not defined the crawler name '%s'." % c      
        
    def _init_crawler(self, cls, param={}):
        cls = import_class(cls)
        
        if cls is None: raise RuntimeError, "Could not loading crawler '%s'." % cls
        
        return cls(**param)
        
    def start(self, t):
        
        site = WebSite(t.header('Site'), '', "worker")
        
        for url in t.list_actions():
            status, url, path = url.split()
            #if status != "200": continue
            for pattern, crawlers in self.url_mapping:
                if not re.match(pattern, path): continue
                self._crawling(site, crawlers, path, url, status)
                break
            else:
                self._crawling(site, self.default_crawlers, path, url, status)
                
    def _crawling(self, site, crawlers, path, url, status):
        
        self.logger.info("Crawling path:%s" % site.real_path(path))
        task = new_task('spider')
        
        task.header('Site', site.hostname)
        
        if url.startswith("http:"): url = urlparse(url).path
        
        for c in crawlers:
            c = self.crawlers[c]
            c.crawl(status, path, url, next_task=task, site=site)
        
        task.status = 'waiting'
        task.remove_empty()

Worker = Analyse