# -*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import time
class login_weibo(object):
    def __init__(self):
         pass
    def __call__(self, client, api, url='', **kw):
      
         client.driver.get("http://www.weibo.com")
         self.client=client
         self.username=kw['user_name']
         self.password=kw['password']
         
         loginName = client.e("div.inp.username input.W_input")
         loginPass = client.e("div.inp.password input.W_input")
         
         loginName.send_keys(self.username)
         loginPass.send_keys(self.password)
         
         submit = client.e("a.W_btn_g ")
         submit.click()
          
         send_weibo = client.e("textarea.input_detail")
         
        
         send_weibo.click()
         send_weibo.send_keys("zheng zai fa ce shi")
          
         send_btn = client.e("a.send_btn")
         send_btn.click()
         
         