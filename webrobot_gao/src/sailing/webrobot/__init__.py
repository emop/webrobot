# -*- coding:utf-8 -*-

from sailing.core import Sailor, new_task, FileTask
#from sailing.core.web.website import WebSite
from sailing.conf import settings
from sailing.common.common import join_path, trackable, is_file
from sailing.common.utils import import_class
from sailing.core.concurrency import TaskScheduler
import logging
from web_client import WebClient
from robot_api import Robot
import thread

class Webrobot(Sailor):
    
    def ready(self):
        #self.http = HTTPClient()
        #self.http.set_proxy(settings.PROXY)
        self.logger = logging.getLogger("webrobot")
        
        self._web_clients = {}
        self._load_actions()
        self.robot_api = Robot()
        #thread.start_new_thread(self.robot_task_tacker, ())
        self.task_pool = None
        
        if settings.WORK_THREAD_COUNT > 1:
            self.task_pool = TaskScheduler(settings.WORK_THREAD_COUNT, self.logger)
        
        
        
    def _load_actions(self, ):
        self.actions = settings.ACTIONS
        for k, v in self.actions.iteritems():
            self.actions[k] = self._init_actions(*v)  

            
    def _init_actions(self, cls, param={}):
        cls = import_class(cls)
        
        if cls is None: raise RuntimeError, "Could not loading crawler '%s'." % cls
        
        return cls(**param)            

    def start(self, t):
        
        client_id = t.header('Client_id')
                
        for l in t.list_actions():
            client_id, action_id, action, args = self._parse_action(l, None)
            if self.task_pool is None:
                self._process_task(client_id, action_id, action, args)
            else:
                self.task_pool.add_task(self._process_task, (client_id, action_id, action, args), client_id)
        
        if self.task_pool is not None:
            self.logger.info("waiting all task done")
            while self.task_pool.pending_count() > 0:
                import time
                time.sleep(3)
            self.logger.info("all task done")
        
                
    def _process_task(self, client_id, action_id, action, args):
        self.logger.info("start to process task for id:%s" % client_id)        
        
        client = self._web_clients.get(client_id, None) 
        if client is None:
            client = WebClient(client_id, "", "clients")
            client.start_client()
            self._web_clients[client_id] = client

        try:
            handler = self.actions.get(action, None)
            self.logger.debug("[%s] %s, args:%s" % (client_id, action, str(args)))
            if handler is not None:
                result = handler(client, self.robot_api, **args)
                self.action_done(action_id, client, result, self.robot_api)
            else:
                self.logger.error("not found sipder action:'%s'", action)
                                    
        except Exception, e:
            self.logger.exception(e)

                
    def action_done(self, action_id, client, result, api):
        self.logger.debug("done [%s] %s on %s" % (result, action_id, client))
        api.action_done(task_id=action_id, result=result)

        
    def _parse_action(self, l, site):
        '''
        return [action, url, local_path, args]
        
        81711368->xxx@passwod=11,bb
        '''
        action_id = 0
        client_id, action = l.split("-->", 1)
        #url, save_as = url.strip(), save_as.strip()  
        
        if ':' in client_id:
            action_id, client_id = client_id.split(":", 1)
        
        if '@' in action:
            action_name, args = action.split("@", 1) 
        else:
            action_name = action
        
        kw = {}    
        for a in args.split(","):
            k, v = a.split("=", 1)
            kw[str(k.strip())] = v.strip()
        
                    
        return (client_id, action_id, action_name, kw)
    
    def robot_task_tacker(self):
        
        self.logger.info("start task tacker...")            
        
        from captcha.http_client import HTTPClient
        import time
        client = HTTPClient()
        while True:
            try:
                data = client.get("http://emopad.sinaapp.com/robot/app/task_list")
                
                self.logger.info("tracker new task:%s" % data)                
                
                if data.strip():
                    t = new_task("webrobot")
                    for line in data.split("\n"):
                        t.add_action(line.strip())
                    t.close()
                    t.status = 'waiting'
                time.sleep(30)
                
                from sailing.conf import settings as CONFIG
                task_list = FileTask.search(CONFIG.APP_NAME, "done", len=15)
                
                for t in task_list:
                    self.logger.info("remove done task:%s" % t._id)       
                    #t.remove()
                
            except:
                pass

    