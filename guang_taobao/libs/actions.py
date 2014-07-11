#-*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import sys
import time
import logging

class SendConpon(object):
    def __init__(self):
         self.logger = logging.getLogger("click")
         pass
    def __call__(self, client, api, url='', **kw):
      
         self.client = client
         self.driver = client.driver
         driver = self.driver
         self.taobao_name = kw['name']        
         self.taobao_passwd = kw['passwd']
         
         from sailing.core import RowTask  
         task = RowTask("link.txt")
         open_link = task.task_list()
         
         import re
         for data in open_link:
#              sid = re.search('sid=(\d+)', data).group(1)
             #data = "http://guang.taobao.com/detail/index.htm?sid=%s" % sid             
             try:
                     self.logger.info("click:%s" % data)
                     client.driver.get(data)
                     time.sleep(1)
                     self.check_login(data)
                     time.sleep(3)
                     self.click_like()
             except Exception, e:
                     self.logger.exception("!!!!!!!Failed to click like !!!!!!!!:%s" % e)
                     
         client.driver.close()
              
    def check_login(self, data):
        if self.client.e("a.nav-user-info"):
            pass
        else:
            loginBtn = self.client.e("a.main-nav-nologin")
            loginBtn.click()
            time.sleep(1)
            
            self.login_user()
            
            #self.client.e("a.nav-user-info")
            self.client.driver.get(data)
            time.sleep(1)
            
    def login_user(self, **kw):
         #safeInput = self.client.e("#J_SafeLoginCheck")
         #safeInput.click() 
         #time.sleep(1)
         
         loginName = self.client.e("#TPL_username_1")
         loginName.send_keys(self.taobao_name)
         time.sleep(1)
            
         loginPass = self.client.e("#TPL_password_1")
         loginPass.send_keys(self.taobao_passwd)
         time.sleep(1)
            
         loginBtn = self.client.e("button#J_SubmitStatic")
         loginBtn.click()
         time.sleep(1)
         
         self.client.screenshot_as_file("login_ok.png")
  
    def click_like(self):
         import datetime
         str_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         self.client.screenshot_as_file("%s.png" % str_time)
         like_btn = self.client.e("span.phx-detail-like__icon")
         if like_btn is not None:
             like_btn.click()
             time.sleep(2)
                 
             flower_btn =self.client.e("a.item-pro-and-con__flower ")
             flower_btn.click()
             time.sleep(2)
         else:
             self.logger.info("Not found like btn")

             
        
       
        
