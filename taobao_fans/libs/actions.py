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
         
         self._login_user()
         
         from sailing.core import RowTask  
         task = RowTask("link.txt")
         open_link = task.task_list()
         
         import re
         for data in open_link:
            # sid = re.search('sid=(\d+)', data).group(1)
             #data = "http://guang.taobao.com/detail/index.htm?sid=%s" % sid             
             try:
                     self.logger.info("click:%s" % data)
                     client.driver.get(data)
                     time.sleep(1)
                     self.click_like()
             except Exception, e:
                     self.logger.exception("!!!!!!!Failed to click like !!!!!!!!:%s" % e)
                     
         client.driver.close()
              
    def _check_login(self, driver):
        
        if not 'taobao.com' in driver.current_url:
            url = "http://www.taobao.com/"
            try:
                driver.get(url)
            except Exception, e:
                self.logger.info("Failed to load page:%s" % e)
        
        try:
            qqWin = driver.find_element_by_css_selector(".login-info .user-nick")
            username = qqWin.text
            
            self.logger.info("login user name:%s" % username)
        except:
            self._login_user()
        
        
    def _login_user(self, **kw):
        
        self.logger.info("start user loging...")
        for i in range(3):
            url = "https://login.taobao.com/member/login.jhtml?"
            try:
                self.driver.get(url)
            except:
                pass
            #label = self.driver.find_element_by_css_selector(".username-field .ph-label")
            #label.click()
            
            nameInput = self.driver.find_element_by_css_selector("#TPL_username_1")
            nameInput.click()
            nameInput.send_keys(self.taobao_name)
            
            #safeInput = self.driver.find_element_by_css_selector("#J_SafeLoginCheck")
            #safeInput.click()    
            #time.sleep(1)
            
            passwdInput = self.driver.find_element_by_css_selector("#TPL_password_1")
            nameInput.click()
            passwdInput.send_keys(self.taobao_passwd)
            
            time.sleep(1)
            submitInput = self.driver.find_element_by_css_selector("#J_SubmitStatic")
            submitInput.click()
            
            time.sleep(2)
            try:
                self.driver.implicitly_wait(2)
                qqWin = self.driver.find_element_by_css_selector(".login-info .user-nick")
                username = qqWin.text
                
                self.logger.info("login user name:%s" % self.taobao_name)
                return
            except:
                self.logger.info("check login failed....")
                
        raise Exception("failed to login:%s" % self.taobao_name)
  
    def click_like(self):
         import datetime
         str_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         self.client.screenshot_as_file("%s.png" % str_time)
         like_btn = self.client.e(".J_Follow")
         if like_btn is not None:
             like_btn.click()
             time.sleep(2)                 
         else:
             self.logger.info("Not found like btn")

             
        
       
        