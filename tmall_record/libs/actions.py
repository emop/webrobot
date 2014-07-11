# -*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import logging
import re
import json
import os
import time
import codecs
import sys

class TmallData(object):
    def __init__(self, ):
        self.logger = logging.getLogger("click")
                
    def __call__(self, client, api, url='', **kw):
        import thread
        self.api = api
        
        self.client = client
        #self.taobao_name = kw['name']        
        #self.taobao_passwd = kw['passwd']
        
        #self.logger.info("start user name:%s, passwd:%s" % (self.taobao_name, self.taobao_passwd))
        
        #self.start_give_conpon = False
        #self._has_more_user = True
        
        #self.logger.info("start login taobao, .......")
        
        driver = client.driver
        self.driver = client.driver
        
        #driver.implicitly_wait(2)
        
        #self._check_login(driver)
        
        resp = self.api.http.post_data("http://cms.emop.cn/api/api_get_record_plan", {})
        resp2 = json.loads(resp, 'utf-8')
        self.logger.info("resp: %s" % resp);
        
        for item in resp2:
            self.logger.info("-start execute item_id %s " % item['item_id']);
            self.item_id = item['item_id']
            
            try:
                 url = "http://detail.tmall.com/item.htm?id=%s" % item['item_id']
                 self._get_month_trade_info(url)
            except Exception, e:
                self.logger.info("start execute item_id except %s" % e)
        
            
    def _open_url(self, url):
        pass
    
    def _get_month_trade_info(self, url):
        
        try:
            self.driver.get(url)
        except Exception, e:
            self.logger.info("Failed to load page:%s" % e)
        
        self.driver.execute_script("window.scrollTo(100, 800)", "")
        time.sleep(2)
        
        self.driver.implicitly_wait(10)
        
        for i in range(3):
            try:
                trade = self.driver.find_element_by_css_selector("#J_TabBar li a[data-index='2']")
                self.driver.execute_script("arguments[0].click()", trade)    
                time.sleep(2)
                break
            except:
                self.logger.info("出错了....")
                pass
        #self.driver.switch_to_window("main")
        

        for i in range(3):
            try:
                self.driver.execute_script("window.scrollTo(100, 2000)", "")
                a = self.driver.find_element_by_css_selector("#J_LinkViewAll")
                a.click()
                time.sleep(2)
                break
            except Exception, e:
                self.logger.info("not found more click:%s" % e)
        
        while True:
            self.driver.execute_script("window.scrollTo(100, 800)", "")
            list = self.driver.find_elements_by_css_selector("#J_showBuyerList tbody tr")
            list = list[1:]
            self.logger.info("==================================")
            date = '2014-01-01 00:00:00'
            for e in list:
                try:
                    cell = e.find_elements_by_css_selector("td")
                    imgs = cell[0].find_elements_by_css_selector("img")
                    self.logger.info("------------")
                    name = cell[0].text
                    title = cell[1].text
                    price = cell[2].text
                    num = cell[3].text
                    date = cell[4].text
                    
                    
                    #如果是淘宝链接特殊处理
                    if not num.isdigit():
                        date = cell[3].text
                        title = cell[4].text
                        
                    self.logger.info("%s --> %s --> %s --> %s --> %s" % (name, title, price, num, date))
                    
                    postdata = {'item_id': self.item_id, 
                                 'record_time': date,
                                 'name': name
                                 }
                    
                    self.update_item_record(postdata);
                    
                except:
                    self.logger.info("fail except....")
            
            
            #只取当天
            exittime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            if date < exittime: 
                self.logger.info("recore——time is execute orver")
                break;
            
            self.driver.execute_script("window.scrollTo(100, 2000)", "")
            next = self.driver.find_element_by_link_text("下一页")
            curpage = self.driver.find_element_by_css_selector("#J_showBuyerList .page-cur")
            
            cur_page = curpage.text
            
            if cur_page == '100':break

            
            self.logger.info("next:" + next.text + ", page:" + cur_page)
            
            self.driver.execute_script(
                    "arguments[0].style[\"display\"] = \"block\";"+
                    "arguments[0].style[\"visibility\"] = \"visible\";"+
                    "return arguments[0];"
                    , next
            )
            
            self.driver.execute_script("arguments[0].click()", next)
             
            time.sleep(2)
            #self.driver.implicitly_wait(2)
    
    def update_item_record(self, data):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.logger.info("update post data:%s" % data)
            
        resp = self.api.http.post_data("http://cms.emop.cn/api/api_update_item_record", data)
        #resp2 = json.loads(resp, 'utf-8')
        #self.logger.info("end for shop_id:%s,api response:%s" % (data['item_id'],json.dumps(resp2, ensure_ascii=False)))
    
        self.logger.info("resp: %s" % resp);
        
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
            if safeInput.is_selected():
                safeInput.click()    
                time.sleep(1)
            
            passwdInput = self.driver.find_element_by_css_selector("#TPL_password_1")
            
            if not passwdInput.is_displayed():
                self.driver.execute_script(
                    "arguments[0].style[\"display\"] = \"block\";"+
                    "arguments[0].style[\"visibility\"] = \"visible\";"+
                    "return arguments[0];", 
                    passwdInput)
            
            passwdInput.send_keys(self.taobao_passwd)
            
            time.sleep(1)
            submitInput = self.driver.find_element_by_css_selector("#J_SubmitStatic")
            submitInput.click()
            
            time.sleep(2)
            try:
                self.driver.implicitly_wait(2)
                qqWin = self.driver.find_element_by_css_selector(".login-info")
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
            
        
        
        
