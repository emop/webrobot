# -*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import logging
import re
import json
import os
import time
import codecs

class SendConpon(object):
    def __init__(self, ):
        self.logger = logging.getLogger("click")
                
    def __call__(self, client, api, url='', **kw):
        import thread
        
        self.client = client
        self.taobao_name = kw['name']        
        self.taobao_passwd = kw['passwd']
        
        self.logger.info("start user name:%s, passwd:%s" % (self.taobao_name, self.taobao_passwd))
        
        self.start_give_conpon = False
        self._has_more_user = True
        
        from sailing.core import RowTask        
        self.taobao_task = RowTask("taobao_user.csv", "done_taobao.csv")        
        if self.taobao_name not in self.taobao_task.done_list:   
            
            thread.start_new(self.give_conpon, ())
            
            #pass
            self.logger.info("start login taobao, .......")
            
            driver = client.driver
            self.driver = client.driver
            
            driver.implicitly_wait(8)
            self._check_login(driver)
            
            for i in range(10):
                if self.start_give_conpon:
                    break
                self.logger.info("waiting to give conpons...")
                time.sleep(2)        
            
            self.empty_retry = 0
            while self._has_more_user and self.empty_retry < 5:
                try:
                    self._start_to_send_conpons()
                    time.sleep(2)
                except Exception, e:
                    self.logger.error("!!!!!!!Failed to send conons!!!!!!!!:%s" % e)
                    #raise
        else:
            self.logger.info("The user is send 50...")
        
        self._has_more_user = False
        client.close()
        self.taobao_task.close()
            
    def _start_to_send_conpons(self):
        
        driver = self.driver
        
        driver.switch_to_default_content()
        
        
        url = "http://ecrm.taobao.com/mallcoupon/got_bonus.htm"
        self.logger.info("start to get bonus:%s" % url)

        driver.get(url)
        
        
        iframe = self.client.e("#couponlist")
        
        if iframe is None:
            return
        
        #self.logger.info("!!!!!!ifame str:%s" % json.dumps(iframe.element))
        #self.logger.info("!!!!!!ifame:%s" % iframe.element)
        driver.switch_to_frame(iframe)
        
        conpons  = self.client.es("#J_coupon_list .row")
        
        if len(conpons) == 0:
            self.empty_retry = self.empty_retry + 1
        else:
            self.empty_retry = 0
            
        self.logger.info("Found conpons:%s, in user:%s" % (len(conpons), self.taobao_name))
        
        self._writer = None
        
        from sailing.core import RowTask
        
        task = RowTask("test.csv", "done.csv")
        
        user_names = task.task_list()
        for row in conpons:
            title = row.e(".td-shop a")
            shop_name = title.text
            self.logger.info(u"shop name:%s" % shop_name)
            if not shop_name == u'青沁堂':
                continue
            
            btn = row.e("a.J_transfer") 
            try:
                sendTo = user_names.next()
            except Exception, e:
                self._has_more_user = False
                self.logger.info(u"all user is send.., e:%s" % e)
                return
            
            self.logger.info(u"number:%s, send to:%s" % (btn.attr('couponnumber'), sendTo))
            btn.click()
            
            time.sleep(0.2)
            
            nameInput = self.client.e("form[name=transfer] #username")            
            nameInput.send_keys(sendTo)
            
            submitInput = self.client.e("form[name=transfer] input[type=submit]")            
            submitInput.click()

            time.sleep(0.2)
            title = row.e(".td-status").text
            self.logger.info("current user info:%s" % title)
            if sendTo in title:
                task.done_task(sendTo)
    
                self.logger.info(u"current sent user:%s" % task.done_count)
            elif self._check_user_not_found():
                close = self.client.e(".ks-dialog a.ks-ext-close")
                if close:
                    close.click()
                task.done_task(sendTo)
            elif self._check_max_send():
                self.taobao_task.done_task(self.taobao_name)
                self._stop_to_send(sendTo)
                break
            elif self._check_not_done():
                title = row.e(".td-status").text
                if sendTo in title:
                    task.done_task(sendTo)
                    self.logger.info(u"current sent user:%s" % task.done_count)
                else:
                    #只截屏，不推出操作。可能是网速太慢，还可以重试。
                    self._stop_to_send(sendTo)
                    self._has_more_user = True 
                    break
            else:
                self.logger.info(u"failed to send user")
                self._stop_to_send(sendTo)
                break  
            
    def _stop_to_send(self, sendTo):
        import datetime
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_screen_path = self.client.real_path("error_%s_%s.png" % (sendTo, time))                
        self.client.driver.get_screenshot_as_file(full_screen_path)
        self._has_more_user = False         
    
    def _check_not_done(self):
        e = self.client.e(".ks-dialog .ks-contentbox")
        if e and u"正在提交" in e.text:
            time.sleep(5)
            return True
        else:
            return False
        
        
    def _check_max_send(self):
        e = self.client.e(".ks-dialog .ks-contentbox")
        if e and u"最多转发" in e.text:
            return True
        else:
            return False
                 
    
    def _check_user_not_found(self, ):
        e = self.client.e(".ks-dialog .ks-contentbox")
        if e and u"昵称不存在" in e.text:
            return True
        else:
            return False
    
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
            url = "https://login.taobao.com/member/login.jhtml?spm=1.1000386.5982201.1.7LXYyx&f=top&redirectURL=http%3A%2F%2Fwww.taobao.com%2F"
            self.driver.get(url)
            
            nameInput = self.driver.find_element_by_css_selector("#TPL_username_1")
            nameInput.send_keys(self.taobao_name)
            
            safeInput = self.driver.find_element_by_css_selector("#J_SafeLoginCheck")
            safeInput.click()    
            time.sleep(1)
            
            passwdInput = self.driver.find_element_by_css_selector("#TPL_password_1")
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
        


        
    def give_conpon(self):
        from sailing.webrobot.web_client import WebClient

        client = WebClient("give_conpon_%s" % self.client.client_id, "", "clients")
        client.start_client()
        
        self._check_get_login(client)
        
        time.sleep(2)
        
        url = "http://my.m.taobao.com/promotion/receie_promotion.htm?&activity_id=33992702&an=3&seller_id=1587750702"
        while self._has_more_user:
            try:
                self.logger.info("get a conpon...(%s)" % self.taobao_name)
                client.driver.get(url)
                
                self.start_give_conpon = True
                time.sleep(2)
                
                uname = client.driver.find_element_by_css_selector(".oran") 
                text = uname.text
                
                self.logger.info("give text:%s" % text)
                if u'量已超限' in text:
                    time.sleep(10)
                elif u"被领取完了" in text:
                    break
            except Exception, e:
                self.logger.info("Get conpon error:%s" % e)
                #有时候会跳出来。
                try:
                    self._check_get_login(client)
                except:
                    self.logger.info("Retry login error......")
                    pass
        
        self.logger.info("Close give conpon client.........")    
        client.close()

    def _check_get_login(self, client):
        url = "http://my.m.taobao.com/promotion/receie_promotion.htm?&activity_id=33992702&an=3&seller_id=1587750702"
        client.driver.get(url)
        
        d = client.driver
        time.sleep(1)
        
        try:
            uname = d.find_element_by_css_selector("#J_UserNameTxt")        
        except:
             self.logger.info("login ok")
             return
        
        uname = d.find_element_by_css_selector("#J_UserNameTxt")  
        uname.clear()   
        uname.send_keys(self.taobao_name)
        
        passwd = d.find_element_by_css_selector("#J_PassWordTxt")   
        passwd.clear()     
        passwd.send_keys(self.taobao_passwd)
        
        submit = d.find_element_by_css_selector("input[type=submit]")        
        submit.click()
        
        full_screen_path = client.real_path("screen.png")
        captcha_path = client.real_path("captcha.png")
        for i in range(3):
            code = self._get_captcha_code(d, {'x':0, 'y':0}, 
                                          full_screen_path, captcha_path)
            if code is None:
                break
            codeInput = d.find_element_by_css_selector("#J_AuthCodeTxt")
            codeInput.send_keys(code)
            
            try:
                d.implicitly_wait(2)
                uname = d.find_element_by_css_selector("#J_UserNameTxt")        
                uname.send_keys(self.taobao_name)
        
                passwd = d.find_element_by_css_selector("#J_PassWordTxt")        
                passwd.send_keys(self.taobao_passwd)
            except:
                pass
            
            submit = d.find_element_by_css_selector("input[type=submit]")        
            submit.click()
            time.sleep(1)                



    def _get_captcha_code(self, driver, p, full_screen_path, captcha_path):
        
        try:
            verifyshow = driver.find_element_by_css_selector(".check-code-img")
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
            
        
        
        