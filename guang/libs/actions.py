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
         
#          from sailing.core import RowTask  
#          task = RowTask("link.txt")
#          open_link = task.task_list()
#          
#          import re
#          for data in open_link:
         url="http://my.taobao.com/UvFN0vGgWMmIuvNTT/album_detail.htm?spm=a310q.2219005.5889385.64.mqKVDi&album_id=4501454834&qq-pf-to=pcqq.group"
                     
         try:
                 self.logger.info("click:%s" % url)
                 client.driver.get(url)
                 client.driver.maximize_window()
                 time.sleep(1)
                 self.check_login(url)
                 time.sleep(3)
                 self.click_actions()
         except Exception, e:
                 self.logger.exception("!!!!!!!Failed to click like !!!!!!!!:%s" % e)
                     
         client.driver.close()
              
    def check_login(self, url):
        if self.client.e("a.user-nick"):
            pass
        else:
           
            loginBtn = self.client.e(".login-info a")
            loginBtn.click()
            time.sleep(1)
            
            self.login_user()
      
            #self.client.e("a.nav-user-info")
#             self.client.driver.get(url)
            self.client.driver.maximize_window()
            time.sleep(1)
            
    def login_user(self, **kw):
         #safeInput = self.client.e("#J_SafeLoginCheck")
         #safeInput.click() 
         #time.sleep(1)
         try:
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
         except Exception, e:
                 self.logger.exception("!!!!!!!Failed to login !!!!!!!!:%s" % e)
  
    def click_actions(self):
         
         try:
             all_list = self.client.es("#J_WaterFall .ks-waterfall-col")
    #          print like_btns
             for all in all_list:
                 like_btns=all.es(".waterfall-item ")
                 for l in like_btns:
                    
                     self.click_like(l)  
                     self.add_album(l)   
                    
        
         except Exception, e:
                self.logger.exception("!!!!!!!Failed to get like_btn!!!!!!!!:%s" % e)           
           
    def click_like(self, l):
         import datetime
         like=l.e("a.like-btn")
         if like is not None:
             like.click()
             str_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
             self.client.screenshot_as_file("%s.png" % str_time)
             time.sleep(2)
                 
         else:
             self.logger.info("Not found like btn")
    
    def add_album(self,l):
         add=l.e("a.add-btn")
         if add is not None:
             add.click()
             time.sleep(1)
            
             if self.client.e(".phx-select-menu__button-caption"):
                 pass 
             else:
                 add_album=self.client.e("#J_FirstAlbum") 
                 add_album.send_keys("my album")  
                 
             confirm=self.client.e("a.phx-add-album__submit")
             confirm.click()
             
             time.sleep(5)
        
       
        