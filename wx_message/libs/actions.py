#-*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import sys
import time
import logging

class SendConpon(object):
    def __init__(self):
         self.logger = logging.getLogger("weixin")
         pass
    def __call__(self, client, api, url='', **kw):
      
         self.client = client
         self.driver = client.driver
         driver = self.driver
         self.wx_name = kw['name']        
         self.wx_passwd = kw['passwd']
         url = "https://mp.weixin.qq.com/"
         try:
             client.driver.get(url)
             client.driver.maximize_window()
             time.sleep(1)
             
             self.check_login()
             time.sleep(1)
             
             self.send_message()
             
         except Exception, e:
             self.logger.exception("!!!!!!!Failed to send message !!!!!!!!:%s" % e)
             return
         
    def check_login(self):
        if self.client.e("#login-form"):
            loginName = self.client.e("#account")
            loginName.send_keys(self.wx_name)
            time.sleep(1)
            
            loginPwd = self.client.e("#password")
            loginPwd.send_keys(self.wx_passwd)
            time.sleep(1)
            
            loginBtn = self.client.e("#login_button")
            loginBtn.click()
            
            self.client.screenshot_as_file("login_ok.png")
        else:
            pass
            
    def send_message(self):
       
        rows = self.client.es(".navigator .textLarge li a")
        rows[2].click()
        time.sleep(1)
        
        winHandleBefore = self.driver.current_window_handle
        
        conpons = self.client.es("#listContainer li")
        for row in conpons:
            row.e("a.msgSenderAvatar").click()
            time.sleep(2)
            
            for winHandle in self.driver.window_handles:
                if winHandle==winHandleBefore:
                    continue
                self.driver.switch_to_window(winHandle)
                
            try:  
                inputArea = self.client.e(".editArea div")
                inputArea.send_keys("hello")
                
                sendBtn = self.client.e(".sendMsg")
                sendBtn.click()
                
                time.sleep(1)
                self.client.screenshot_as_file("send_ok.png")
                
                self.driver.close()
                time.sleep(1)
                self.driver.switch_to_window(winHandleBefore)
            except Exception, e:
                self.logger.info("falied send message:%s" % e)
                return
        
                   