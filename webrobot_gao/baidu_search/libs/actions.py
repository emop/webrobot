# -*- coding: utf8 -*-

import time

class BaiduSearch(object):
    def __init__(self):
        pass
    
    def __call__(self, client, api, **kw):
        pass
    
        self.client = client
        
        client.driver.get("http://www.baidu.com")
        
        #input = client.e("#kw")
        #input.clear()
        #input.send_keys(kw['keyword'])
        
        #submit = client.e("#su")
        #submit.click()
        
        #path = client.real_path("screen.png")
        
        #client.screenshot_as_file("screen.png")
        
        #iframe = client.e("#iframe")
        #client.switch_to_frame(iframe)
        
        #self.checkBackgroundButton(self)
        
        self.checkBackgroundButton();

            
        loginBox = client.e("#passport-login-pop")
        
        if loginBox:
            
            loginName = client.e("#TANGRAM__PSP_10__userName")
            passWord = client.e("#TANGRAM__PSP_10__password")
            login = client.e("#TANGRAM__PSP_10__submit")
            
            loginName.send_keys("gaomingjun.main@qq.com")
            
            time.sleep(1)
            
            passWord.send_keys("lovetheway!!")
            
            login.click()
        
        #client.driver.get("http://www.baidu.com")
        time.sleep(2)
        
        self.checkBackgroundButton();
            
            
        bgs = client.es("#s_bg_allimgs li")
        
        for bg in bgs:
            
            bg.click()
            time.sleep(0.5)
            
        #self.checkBackgroundButton(self)
            
    def checkBackgroundButton(self):
         
        backgroundButton = self.client.e("#s_bg_entrance a")
         
        if backgroundButton is None:
            lb = self.client.e("#lb")
            lb.click()
         
        else:
            backgroundButton.click()

            
            
            
        
            
            
            
            
        
        