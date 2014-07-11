#-*- coding: utf8 -*-

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
		url_login = "https://login.taobao.com/member/login.jhtml"
		url_emop = "http://www.emop.cn/20131111/74"
		
		self.open_url(url_login)
		self.login_user()
		self.open_url(url_emop)
		self.collect_coupon()
		
		
	def open_url(self, openurl):
		try:
			self.driver.get(openurl)
			time.sleep(3)
		except:
			self.logger.warning("open the sina host timeout")
		return self.driver.current_url
		
	def check_login(self, data):
		if self.client.e("a.nav-user-info"):
			pass
		else:
			loginBtn = self.client.e("a.main-nav-nologin")
			loginBtn.click()
			time.sleep(1)

			self.login_user()

			#self.client.e("a.nav-user-info")
			self.client.driver.get(data)
			time.sleep(1)
            
	def login_user(self):
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
		
	def collect_coupon(self):
		data = self.client.es(".co_url a")
		
		for d in data:
			d.click()
			self.driver.close()
			time.sleep(2)
			
			
       
        
