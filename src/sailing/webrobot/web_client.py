from __future__ import with_statement
'''

A webclient, It's bind with a opening browser. It used to control the browser
action
 
@author: deonwu
'''

from sailing.common.common import join_path, dir_name, make_path, exists_path
from contextlib import closing
import logging
from sailing.conf import settings
import thread
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver

class MyWebDriver(WebDriver):
    def start_session(self, *args, **kw):
        if self.session_id == -1:
            super(MyWebDriver, self).start_session(*args, **kw)
    
class WebClient(object):
    
    def __init__(self, client_id, local_path='', work_root='', meta={}):
        self.client_id = client_id or 'unknown.site'
        self.local_path = local_path or client_id
        self.work_root = work_root
        
        self.logger = logging.getLogger("webclient")

        self.props = {}
        self._load_props()
        self._is_closed = False
        pass
    
    def real_path(self, url):
        
        if self.work_root:
            path = join_path(self.work_root, self.local_path, url)
        else:
            path = join_path(self.local_path, url)
            
        return path.replace(":", "_")
    
    
    def start_client(self):
        
        capability = {'browserName': 'chrome',
                     }
       
        capability = {'browserName': 'phantomjs',
                     }        
        chrome_options = {
                      #"chrome.switches": ["--user-data-dir=%s" % self.client_id, "--incognito"],
                      'args': ["--incognito"],
                      #'chrome.args': ["--user-data-dir=%s" % self.client_id, "--incognito"],
                      }
        
        capability['chromeOptions'] =  chrome_options # 'chromeOptions':
        
        isRemote = False
        
        if "local" in self.client_id or settings.BROWSER_NAME == 'local':
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--incognito')
            self.driver = webdriver.Chrome(chrome_options=options, service_log_path='chrome.log')
        elif settings.BROWSER_NAME == 'firefox':
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--incognito')
            self.driver = webdriver.Firefox()        
        elif "phantomjs" == settings.BROWSER_NAME:
            from selenium import webdriver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            
            capability = DesiredCapabilities.PHANTOMJS
            
            agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'
            capability['phantomjs.page.settings.userAgent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31"
            self.driver = webdriver.PhantomJS(desired_capabilities=capability)            
        else:
            isRemote = True
            self.driver = MyWebDriver(settings.WEB_HUB_URL,
                                      desired_capabilities=capability)
        
        started = False
        if self.props.get('web_session_id', 0) and isRemote:
            self.logger.info("start client with old session:%s" % self.props['web_session_id'])
            self.driver.session_id = self.props['web_session_id']
            
            try:
                #started = self.driver.is_online()
                cur_url = self.driver.current_url
                self.logger.info("current session url:%s" % cur_url)
            except Exception, e:
                started = False
                self.logger.info("Failed to attched old session." )
            
        if not started:            
            self.logger.info("create new session...")

            if isRemote:
                self.driver.session_id = -1            
                self.driver.start_session(capability)
                
            self.props['web_session_id'] = self.driver.session_id
            
            self.driver.delete_all_cookies()
            self.logger.info("create new session id:%s" % self.props['web_session_id'])

            self._save_props()
            
        self.driver.implicitly_wait(10)
        try:
            self.driver.set_page_load_timeout(10)
        except:
            pass
        
        if isRemote:
            thread.start_new_thread(self.heart_beat_check, (self.driver.session_id, ))
            
    
    def _load_props(self):        
        conf_path = self.real_path("client.conf")
        
        if not exists_path(conf_path):
            return
        
        with closing(open(conf_path, 'r')) as links:
            for l in links:
                #end of header
                if not l.strip(): break
                if l.startswith("#") or l.count(':') == 0: continue
                name, value = l.split(":", 1)
                self.props[name.strip()] = value.strip()
    
    def _save_props(self):
        
        conf_path = self.real_path("client.conf")  
        
        make_path(dir_name(conf_path))
        
        fd = open(conf_path, 'w')
        
        for k, v in self.props.iteritems():
            fd.write("%s:%s\n" % (k, v))
            fd.write("\n")
        
        fd.close()
        
    def is_closed(self):
        return self._is_closed
        
    def heart_beat_check(self, session_id):
        self.driver.implicitly_wait(10)
        
        while not self.is_closed() and self.props['web_session_id'] == session_id:
            self.logger.info("current opening url:%s" % self.driver.current_url)
            time.sleep(10)
            
        self.logger.info("the client is closed")
    
    def close(self):
        self._is_closed = True
        self.driver.quit()
    
    def e(self, locator):
        try:
            node = self.driver.find_element_by_css_selector(locator)
            return ElementWraper(node)
        except NoSuchElementException, e:
            self.logger.info("Not found element by '%s', error:%s" % (locator, e))
        
        return None
    
        
    def es(self, locator):
        try:
            nodes = self.driver.find_elements_by_css_selector(locator)
            
            return [ ElementWraper(el) for el in nodes ]
        except NoSuchElementException, e:
            self.logger.info("Not found element by '%s', error:%s" % (locator, e))
        
        return []
    
    def screenshot_as_file(self, path):
        real_path = self.real_path(path)
        try:
            self.driver.get_screenshot_as_file(real_path)
            self.logger.info("save screenshot to:%s" % real_path)
        except Exception, e:
            self.logger.warn("save screenshot error:%s" % e)
        
    
class ElementWraper(object):
    
    def __init__(self, o):
        self.element = o
        
        
    def val(self, val = None):
        if val is not None:
            self.element.clear()
            self.element.send_keys(val)
        return self.element.text
    
    
    def attr(self, name, val = None):
        if val is not None:
            raise Exception("not support set attr")
            #self.element.get_attribute(name)
        return self.element.get_attribute(name)
    
    def __getattr__(self, name):
        return getattr(self.element, name)
    
    def e(self, locator):
        try:
            node = self.element.find_element_by_css_selector(locator)
            return ElementWraper(node)
        except NoSuchElementException, e:
            logging.info("Not found element by '%s', error:%s" % (locator, e))
        
        return None
    
        
    def es(self, locator):
        try:
            nodes = self.element.find_elements_by_css_selector(locator)
            
            return [ ElementWraper(el) for el in nodes ]
        except NoSuchElementException, e:
            logging.info("Not found element by '%s', error:%s" % (locator, e))
        
        return []
    
    @property
    def id(self):
        return self.element.id    
         
