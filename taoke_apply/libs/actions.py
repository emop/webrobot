#-*- coding: utf8 -*-

import sys
import time,os
import logging
import json

from test.test_socket import try_address
from _ast import TryExcept

class TaokeApply(object):
    def __init__(self):
        self.logger = logging.getLogger("click")
        pass
    def __call__(self, client, api, url='', **kw):
      
        self.client = client
        self.driver = client.driver
        self.api = api
         
        self.alimama_name = 'star@littlefun.net'
        self.alimama_passwd = 'jinsiyan118JSY'
        self.login_type = 'alimama'
        
        self.taobao_name = 'x'
        self.taobao_passwd = 'x'
        
        self.apply_plan_url = 'http://pub.alimama.com/index.htm?spm=0.0.0.0.a2DtbH#!/promo/self/items?q=%s&toPage=%s'
        self.currentApplyTimes = 0;
        
        self.last_iframe_postion = None
        
        self.apply_content = '你好，冒泡网淘客申请加入计划；冒泡网【http://shop.emop.cn】由淘客平台转型 CPC(按点击付费)模式，超低点击单价0.3，平台两万微博主继续为您提供优质精准 的流量点击，欢迎咨询加入，联系QQ675942879；'

        from sailing.core import RowTask  
        task = RowTask("apply_keyword.txt")
        apply_keyword = task.task_list()
            
        for page in range(100):    
            for ak in apply_keyword:
                try:
                    self.logger.info("------start, open apply url to apply keyword: %s, page: %s" % (ak.encode('GBK', 'ignore'), page+1))
                    self.open_apply_page(ak, page+1)
                    self.execute_has_campaign()   
                    self.execute_apply()
                except:
                    self.logger.info("----------------except=>execute apply keyword: %s, page: %s" % (ak, page+1))
                    
            
         
    def execute_has_campaign(self):
        #print '----------------location=>execute_has_campaign-------------------------'
        time.sleep(3)
        campaign_list = self.es("a.has-campaign")
        #print "curent node %s" % campaign_list
        try:
            for campaign in campaign_list:
                self.logger.info('--------This is one campaign of campaign_list, campaign click before-----------')
                self.driver.execute_script(
                    "arguments[0].style[\"display\"] = \"block\";"+
                    "arguments[0].style[\"visibility\"] = \"visible\";"+
                    "return arguments[0];"
                    , campaign
                    )
                self.driver.execute_script("arguments[0].click()", campaign)
                #campaign.click()
                self.logger.info('campaign click after, this text is: %s ' % campaign.text.encode('GBK', 'ignore'))
                
                time.sleep(2);
                
        except:
            self.logger.info('campaign apply click location except, continue')
                
    def execute_apply(self):
        xpath = '''
        a[atp={ptype:'items',ctype:'campaign_apply'}]
        '''
        #{ptype:'items',ctype:'campaign_detail'}
        #a[@atp="{ptype:'items',ctype:'campaign_apply'}"]
        apply_list = self.es(".table-child-tr table tbody tr")
        for apply in apply_list:
            self.client.driver.implicitly_wait(1)
            try:
                bt = apply.es(".color-blue")[1]
                mx = bt.get_attribute('mx-click')
                self.logger.info("apply click text: %s, mx-click: %s" % (bt.text, mx))
                if mx is not None:
                    self.execute_apply_click(bt, mx)
                else:
                    self.logger.info("This apply campaign is appling! continue")
            except:
                self.logger.info("This apply campaign occured excepte! continue")
                
            
    def execute_apply_click(self, bt, mx):
        mx = mx.replace("}", '')
        mxs = mx.split(",");
        data = {'campaign_id': mxs[0].split(":")[1], 
                'shop_id': mxs[1].split(":")[1],
                'status':'ok',
                }
        #status = self.update_alimama_taoke_apply(data)
        #if status == 'ok':
        bt.click()
        time.sleep(1)
        textarea = self.e('#J_applyForm textarea')
        textarea.send_keys(self.apply_content.decode("utf-8"))
        
        submit = self.driver.find_element_by_link_text("提交申请")
        self.logger.info("submit button text: %s", submit.text.encode('GBK', 'ignore'))
        submit.click()
        self.update_alimama_taoke_apply(data)
            
        #else:
        #    self.logger.info('apply do not need apply')
        
            
    def update_alimama_taoke_apply(self, data):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.logger.info("update apply post data:%s" % data)
                
        resp = self.api.http.post_data("http://mty365.com/mtyapi/api_alimama_taoke_apply", data)
        resp2 = json.loads(resp, 'utf-8')
        self.logger.info("end for shop_id:%s,api response:%s" % (data['shop_id'],json.dumps(resp2, ensure_ascii=False)))
        
        if resp2['status'] == 'ok':
            return 'ok'
        else:
            return 'err'
        
         
    def open_apply_page(self, keyword, page):
        self.client.driver.implicitly_wait(3)
        try:
            self.driver.get(self.apply_plan_url % (keyword, page))
                    
            self.client.driver.implicitly_wait(2)
            
            if not self._check_is_login(keyword):
                self.logger.info("----------------------------This page is not login, to login and retry--------------------")
                if self.login_type == 'alimama':
                    self.login_with_alimama(keyword)
                    
                    self.client.driver.implicitly_wait(2)
                    self.driver.get(self.apply_plan_url % (keyword, page))
                else:
                    self.login_with_taobao(keyword)
            else:
                self.logger.info("----------------------------This page have login--------------------")
        except Exception, e:
            #pass
            self.logger.info("----------------------------This page except:%s--------------------" % e)
        time.sleep(3)
        
    def _check_is_login(self, kw):
        self.client.driver.implicitly_wait(2)
        item = self.e(".menu-hd a")
        self.client.driver.implicitly_wait(10)
        self.logger.info("----------------------------login item %s--------------------" % item)
        return item is not None
    
    def login_with_alimama(self, kw):
        nav = self.es(".login-panel .nav li")
        self.client.driver.implicitly_wait(2)
        nav[1].click()
        
        time.sleep(0.5)
        
        self.logger.info("start user with alimama loging...")
        
        for i in range(2):
            cur_url = self.client.driver.current_url
            if 'www.alimama.com/member/login' not in cur_url:
                url = "http://www.alimama.com/member/login.htm?forward=http%3A%2F%2Fu.alimama.com%2Funion%2Fcard%2FShopKeeperDetail.htm"
                self.client.driver.get(url)
                time.sleep(1)
            self._switch_to_login_frame("#J_mmLoginIfr")
            
            nameInput = self.e("#J_logname")
            
            nameInput.send_keys(self.alimama_name)
                        
            passwdInput = self.e("#J_logpassword")
            passwdInput.send_keys(self.alimama_passwd)
            
            time.sleep(1)
            submitInput = self.e("#J_submit")
            submitInput.click()
            
            time.sleep(2)
            
            try:
                self.client.driver.implicitly_wait(2)
                self.client.driver.switch_to_default_content()
                
                item = self.e("div.menu-hd a")
                username = item.text
                
                self.logger.info("login user name:%s" % username.encode('GBK', 'ignore'))
                return
            except:
                self.logger.info("check login failed....")
                
        raise Exception("failed to login:%s" % self.taobao_name)    
        
    def login_with_taobao(self, kw):
        self.login_with_iframe(kw)
        self.client.driver.switch_to_default_content()
    
    def login_with_iframe(self, kw):
        self.logger.info("start user with taobao loging...")
        for i in range(3):
            cur_url = self.client.driver.current_url
            if 'www.alimama.com/member/login' not in cur_url:
                url = "http://www.alimama.com/member/login.htm?forward=http%3A%2F%2Fu.alimama.com%2Funion%2Fcard%2FShopKeeperDetail.htm"
                self.client.driver.get(url)
                
            self._switch_to_login_frame()
            
            nameInput = self.e("#TPL_username_1")
            nameInput.send_keys(self.taobao_name)
            
            safeInput = self.e("#J_SafeLoginCheck")
            safeInput.click()    
            time.sleep(1)
            
            passwdInput = self.e("#TPL_password_1")
            passwdInput.send_keys(self.taobao_passwd)
            
            time.sleep(1)
            submitInput = self.e("#J_SubmitStatic")
            submitInput.click()
            
            time.sleep(2)
            
            r = self.check_other_validate()
            if not r:
                raise Exception("failed to login:%s" % self.taobao_name)
            
            try:
                self.client.driver.implicitly_wait(2)
                self.client.driver.switch_to_default_content()
                
                item = self.e("a.account")
                username = item.text
                
                self.logger.info("login user name:%s" % username)
                return
            except:
                self.logger.info("check login failed....")
                
        raise Exception("failed to login:%s" % self.taobao_name)
    
    def _switch_to_login_frame(self, selector="[name=taobaoLoginIfr]"):
        self.client.driver.implicitly_wait(2)
        iframe = self.e(selector)
        self.client.driver.implicitly_wait(10)
        if iframe is not None:
            self.last_iframe_postion = iframe.location
            self.client.driver.switch_to_frame(iframe)
    def e(self, l):
        return self.client.e(l)
    
    def es(self, l):
        return self.client.es(l)
    