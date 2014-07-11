# -*- coding:utf-8 -*-

from sailing.core import Sailor, new_task
from sailing.core.web.website import WebSite
from http_client import HTTPClient
from sailing.conf import settings
from sailing.common.common import join_path, trackable, is_file
from sailing.common.utils import import_class
import logging

class Spider(Sailor):
    pass
    
    def ready(self):
        self.http = HTTPClient()
        self.http.set_proxy(settings.PROXY)
        self.logger = logging.getLogger("Spider")
        
        self._load_actions()
        
        
    def _load_actions(self, ):
        self.actions = settings.ACTIONS
        for k, v in self.actions.iteritems():
            self.actions[k] = self._init_actions(*v)  

        self.actions['GET'] = self.http_get
        self.actions['POST'] = self.http_post
            
    def _init_actions(self, cls, param={}):
        cls = import_class(cls)
        
        if cls is None: raise RuntimeError, "Could not loading crawler '%s'." % cls
        
        return cls(**param)            

    def start(self, t):
        
        site = WebSite(t.header('Site'), "", "worker")
        
        next_task = new_task('worker')
        next_task.header('Site', t.header('Site'))
        
        for l in t.list_actions():
            action, url, save_as, args = self._parse_action(l, site)
            try:
                handler = self.actions.get(action, None)
                self.logger.debug("[%s] %s --> %s, args:%s" % (action, url, save_as, str(args)))
                if handler is not None:
                    handler(site, self.http, next_task, url, save_as, *args)
                else:
                    self.logger.error("not found sipder action:'%s'", action)
                    
            except Exception, e:
                self.logger.exception(trackable(u"Exception on task '%s'" % e))
        self.http.close()
            
        next_task.status = 'waiting'
        
    def _parse_action(self, l, site):
        '''        
        return [action, url, local_path, args]
        '''
        url, save_as = l.split("==>", 1)
        url, save_as = url.strip(), save_as.strip()  
        
        if '@' in save_as:
            save_as, actions = save_as.split("@", 1) 
        else:
            actions = ''
        
        if not url.startswith("http:"):
            url = "http://%s%s" % (site.hostname, url)
            
        (action, args) = ('GET', [])        
        if actions:
            actions = actions.split(":")
            action, args = actions[0], actions[1:]
        
        return (action, url, save_as, args)
        
    def http_get(self, site, http, next_task, url, save_as, *args):
        local_path = self._save_as(site, save_as)
        if not is_file(local_path):
            status = http.download(url, local_path)
            next_task.add_action("%s %s %s" % (status, url, save_as))
        else:
            self.logger.info("exist local file:%s->%s" % (url, local_path))
        
    def http_post(self, site, http, next_task, url, save_as, data, *args):
        local_path = self._save_as(site, save_as)
        status = http.post(url, local_path, data)
        next_task.add_action("%s %s %s" % (status, url, save_as))

    def _save_as(self, site, path):
        #path = path.strip().split("/")
        return site.real_path(path)
    