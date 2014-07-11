# -*- coding: utf8 -*-

import time
import logging

class GetShopTaokeInfo(object):
    def __init__(self, ):
        self.logger = logging.getLogger("click")
    
    def __call__(self, client, api, **kw):
        """
        client -- 
        client
        api --        
        """
        
        self.client = client
        
        self.alimama_name = 'star@littlefun.net'
        self.alimama_passwd = 'jinsiyan118JSY'
        self.login_type = 'alimama'
        
        self.taobao_name = 'x'
        self.taobao_passwd = 'x'
        
        self.apply_plan_url = kw['apply_plan_url']
        
        self.last_iframe_postion = None
        self.rate_node = None
        
        
        self.client = client
        for i in range(2):
            self.open_shop_link(kw['shop_id'])
            
            client.screenshot_as_file("shop_%s.png" % kw['shop_id'])
            
            self.client.driver.implicitly_wait(2)
            if self.e("a.account") is not None:
                self._update_emop_shop_data(kw['shop_id'], {'commission_rate': '-1'}, api)                
            elif not self._check_is_login(kw):
                if self.login_type == 'alimama':
                    self.login_with_alimama(kw)
                else:
                    self.login_with_taobao(kw)
            else:
                data = self.get_shop_taoke_info(kw)
                self._update_emop_shop_data(kw['shop_id'], data, api)
                break        

    def open_shop_link(self, shop_id):
        self.logger.info("============ start for commission rate,shop_id: %s ============" % shop_id)
        self.client.driver.implicitly_wait(5)
        shop_url = "http://shop%s.taobao.alimama.com/" % shop_id
        try:
            self.client.driver.get(shop_url)
        except:
            pass
        time.sleep(3)
        
    
    def get_shop_taoke_info(self, kw):
        
        shop_info  = self.e(".shop-infos .attr .blue-link").text
        
        row = self.e(".shop-campaign tbody tr")
        #conpons = self.es(".shop-campaign tbody tr")
        tds = row.es('td')
        
        name = tds[0].text # row.e("td:eq(0)")
        commission_rate = tds[3].text #row.e("td:eq(3)")
        self.logger.info("============ end for commission rate: %s,shop_id: %s ============" % (commission_rate,kw['shop_id']))

        #res = []
        #for row in conpons:
            #if row == conpons[0]:
               #continue
            #tds = row.es('td')
            #average_commission = tds[3].text
            #res.append(average_commission)
            
        #max_commission = max(res)
        #self.logger.info("max average_commission:%s" % max_commission)
        
        #for row in conpons:
            #if row == conpons[0]:
               #continue
            #tds = row.es('td')
            #average_commission = tds[3].text
            
            #if average_commission == max_commission:
               #clickbtn = row.e("a.blue-link")
               #clickbtn.click()
               #time.sleep(1)
               #extend_link = self.client.driver.current_url
               #self.logger.info("extend_link:%s" % extend_link)
            #break
        self.logger.info("============ start for modify commission rate,shop_id: %s ============" % kw['shop_id'])
        self.client.driver.implicitly_wait(5)
        try:
            self.client.driver.get(self.apply_plan_url)
        except:
            pass
        time.sleep(2)
        
        
        try:
            rows=self.es(".med-list-tab ul li a")
            self.client.driver.implicitly_wait(5)
            self.rate_node = rows[2]
        except:
            self.logger.info("not find shop plan info....")
        
        modify_commission = 0
        modify_commission_time = ''
           
        if self.rate_node is not None:
                self.rate_node.click()
                time.sleep(2)
                
                first_row = self.e(".med-table.med-list-s tbody tr")
                if first_row.e('td .attention') is not None:
                    pass
                else:
                    first_tds = first_row.es('td')
                    modify_commission_time = first_tds[0].text
                    modify_commission = first_tds[1].text
        else:
            pass 
            
        self.logger.info("============ end for modify commission rate: %s,shop_id: %s ============" % (modify_commission,kw['shop_id']))
        
        if modify_commission>0:
           modify_commission_rate=modify_commission.strip(' %')
        else:
           modify_commission_rate= modify_commission
           
        data = {'commission_rate': commission_rate.strip(' %'), 
                'modify_commission_rate': modify_commission_rate,
                'modify_commission_time': modify_commission_time,
                'commission_name': name.encode("utf8"),
                'shop_name': shop_info.encode("utf8")
                
                }
        self.logger.info("shop info:%s" % str(data))  
        return data
        
        
    
    def _update_emop_shop_data(self, shop_id, data, api):
        
        self.logger.info("update shop:%s, rate:%s" % (shop_id, data['commission_rate']))
        data['shop_id'] = shop_id
                
        resp = api.http.post_data("http://web.emop.cn/queue/update_shop_commission_rate", data)
        
        self.logger.info("end for shop_id:%s,emop response:%s" % (shop_id,resp))
        self.logger.info("\r\n")  
        self.logger.info("\r\n")  

    def _check_is_login(self, kw):
        self.client.driver.implicitly_wait(2)
        item = self.e("#J_loginInfo a")
        self.client.driver.implicitly_wait(10)
        
        return item is not None #and self.taobao_name in item.text

    def _switch_to_login_frame(self, selector="[name=taobaoLoginIfr]"):
        self.client.driver.implicitly_wait(2)
        iframe = self.e(selector)
        self.client.driver.implicitly_wait(10)
        if iframe is not None:
            self.last_iframe_postion = iframe.location
            self.client.driver.switch_to_frame(iframe)
            
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
                
                item = self.e("a.account")
                username = item.text
                
                self.logger.info("login user name:%s" % username)
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
    
    def check_other_validate(self):
        """检查是否需要手机验证码，什么的
        """
        #self._switch_to_login_frame()
        
        self.client.driver.implicitly_wait(10)


        validate = self.e(".aq_def_overlay iframe")
        if validate is None:
            return True
        else:
            p = validate.location
            self.last_iframe_postion['x'] = self.last_iframe_postion['x'] + p['x']
            self.last_iframe_postion['y'] = self.last_iframe_postion['y'] + p['y']
            
            self.client.driver.switch_to_frame(validate)
        
        self.logger.info("Start other validate, try mobile phone firstly....")
        
        validate = self.e("#J_ValidateSelect")
        opt = validate.es("option")
        opt = len(opt) > 1 and opt[1] or opt[0]
        opt.click()
        
        time.sleep(1)
        
        sendCode = self.e("#SendPhoneCode")
        if sendCode is not None and sendCode.is_displayed():
            sendCode.click()
        
        validateCode = self._get_captcha_code(self.client.real_path("login_screen.png"), 
                                              self.client.real_path("login_captcha.png"))
        
        codeInput = self.e("#J_CodeInput")
        if validateCode is not None and codeInput is not None:
            codeInput.val(validateCode)
            submit = self.e("#J_SubmitBtn")
            submit.click()
            return True
        else:
            self.logger.info("failed to get validate code")    
            
        return False
            
    def _get_captcha_code(self, full_screen_path, captcha_path):
        driver = self.client.driver
        if self.last_iframe_postion is not None:
            p = self.last_iframe_postion
        else:
            p = {'x':0, 'y':0}
            
        try:
            verifyshow = driver.find_element_by_css_selector("#J_Other .mod")
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
            
        from sailing.webrobot.captcha import get_captcha, create_captcha_image
        create_captcha_image(full_screen_path, captcha_path, new_box)
        

        print "starting get captcha: %s" % (captcha_path, )        
        data = get_captcha(captcha_path, )
        print "captcha response:%s" % str(data)
    
        if data['status'] == 'ok':
            code = data['captcha']
            return code
        
        return None            

    def e(self, l):
        return self.client.e(l)
    
    def es(self, l):
        return self.client.es(l)

    