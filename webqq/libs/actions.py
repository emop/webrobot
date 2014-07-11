# -*- coding: utf8 -*-
import logging
import re
import json
import os
import time

class LoginUqude(object):
    def __init__(self, ):
        self.logger = logging.getLogger("webqq")
        
    def __call__(self, client, api, username='', passwd=''):
        self.logger.info("start login webqq, username:%s, ......." % username)
        
        driver = client.driver
        driver.switch_to_default_content()
        
        if not 'qq.com' in driver.current_url: # != "http://web2.qq.com":
            driver.get("http://web2.qq.com")
    
        # find the element that's name attribute is q (the google search box)
        #inputElement = driver.find_element_by_name("q")
        try:
            qqWin = driver.find_element_by_css_selector(".eqq_window")
            qqNick = driver.find_element_by_css_selector(".eqq_window .EQQ_myNick")
            
            title = qqNick.get_attribute("title")
            if username in title:            
                self.logger.info("the qq is logined in current window, title:%s" % username)
                return
        except:
            pass
        
        print "find app id..."
        inputElement = driver.find_element_by_css_selector("div[appId='50']")
        
        print "ele:%s" %  inputElement  
        inputElement.click()
        
        time.sleep(2)
        
        iframe = driver.find_element_by_css_selector("#ifram_login")
        p = iframe.location
        driver.switch_to_frame(iframe)
        
        name = driver.find_element_by_css_selector("#u")
        name.clear()
        name.send_keys(username)
        
        passwd_input = driver.find_element_by_css_selector("#p")
        passwd_input.clear()
        passwd_input.send_keys(passwd)        
        
        verifycode = driver.find_element_by_css_selector("#verifycode")
        
        login_button = driver.find_element_by_css_selector("#login_button")
        
        verifyshow = driver.find_element_by_css_selector("#verifyshow")
        
        full_screen_path = client.real_path("screen.png")
        captcha_path = client.real_path("captcha.png")
        
        for i in range(3):
            time.sleep(2)
            code = self._get_captcha_code(driver, p, full_screen_path, captcha_path)
            if not code:
                break
            else:
                verifycode.send_keys(code)
                login_button.click()
        
        print "login done"
        
    def _get_captcha_code(self, driver, p, full_screen_path, captcha_path):
        
        try:
            verifyshow = driver.find_element_by_css_selector("#verifyshow")
        except:
            print "Not found vrify code"
            return None
        
        driver.get_screenshot_as_file(full_screen_path)    
        vp = verifyshow.location
        s = verifyshow.size
        
        #box = (left, top, left+width, top+height)
        left = p['x'] + vp ['x']
        top = p['y'] + vp['y']
        new_box = (int(left), int(top), int(left + s['width']), int(top + s['height']))
            
        self.save_screenshot_img(full_screen_path, captcha_path, new_box)
        
        from sailing.webrobot.captcha import get_captcha

        print "starting get captcha: %s" % (captcha_path, )        
        data = get_captcha(captcha_path, )
        print "captcha response:%s" % str(data)
    
        if data['status'] == 'ok':
            code = data['captcha']
            return code
        
        return None
        
    def save_screenshot_img(self, input_path, out_path, box):
        from PIL import Image
        
        # size is width/height
        img = Image.open(input_path)
        #box = (2407, 804, 71, 796)
        area = img.crop(box)    
        area.save(out_path, 'png')
        #img.close()
        pass
    
class SendWeibo(object):
    def __init__(self, ):
        self.logger = logging.getLogger("webqq")
        
    def __call__(self, client, api, lib_id='', **kw):
        driver = client.driver

        driver.switch_to_default_content()
        
        inputElement = driver.find_element_by_css_selector("div[appId='2']")
        
        inputElement.click()
    
        time.sleep(1)
        iframe = driver.find_element_by_css_selector("iframe.iframeApp")
        driver.switch_to_frame(iframe)
        
        try:
            login_btn = driver.find_element_by_css_selector("#qlogin_show a.face")
            login_btn.click()
            time.sleep(2)
        except Exception, e:
            print "click login face, error:%s" % e
            
        text = driver.find_element_by_css_selector("#msgTxt")
        text.clear()
        #text.send_keys("测试，测试， 测试")
        import datetime
        
        data = api.get_weibo_lib(lib_id=lib_id)
        
        self.logger.info("weibo data, lib id:%s, :%s" % (lib_id, str(data)))
        
        text.send_keys(data['data']['text'])
    
        sendBtn = driver.find_element_by_css_selector("input.sendBtn")
        sendBtn.click()
        
        
        #msgTxt
        #inputElement.click()
        
        time.sleep(2)
