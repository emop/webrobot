#-*- coding: utf8 -*-

import sys
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains

class SendConpon(object):
	def __init__(self):
		self.logger = logging.getLogger("click")
		pass
	def __call__(self, client, api, url='', **kw):
		self.client = client
		self.driver = client.driver
		driver = self.driver
		self.shop_nick=""
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
		data = self.client.es(".fs_list a img")
		
		
		for d in data:
			try:
				self.shop_nick=self.driver.execute_script('return arguments[0].getAttribute("alt")',d)
				print self.shop_nick
				d.click()
				time.sleep(2)
				
				winHandlef=self.driver.window_handles
				self.driver.switch_to_window(winHandlef[-1])
				time.sleep(2)		
				self.collect_shop()
				
				winHandleindex=self.driver.window_handles
				self.driver.switch_to_window(winHandleindex[-1])
				
			except:
				pass
# 			self.driver.switch_to_window()
	
	def collect_shop(self):

		try:
			if self.e(".extra-info") is not None:
				row=self.e(".extra-info")
				self.driver.execute_script('arguments[0].setAttribute("style","display:block")',row)
	 
				time.sleep(2)
				collect_url=self.e("#xshop_collection_href span")
				collect_url.click()
			else:
				co=self.e(".line-right .shop-collect")
				co.click()
 			
		except Exception,e:
			print "failed to collect shop",e
			
		time.sleep(1)
		self.client.screenshot_as_file("collect_shop_ok.png")
#  		
		try:
			inputser = self.e("input#mq")
			inputser.send_keys(self.shop_nick)
			if self.e("#J_SearchBtn") is not None:
				btn=self.e("#J_SearchBtn")
			else:
				btn=self.e(".btn-search")
			btn.click()
		except:
			pass

 		
 		time.sleep(2)
 		try:
			pro_list=self.es("#J_ItemList .product .productImg-wrap a img")[0]
			pro_list.click()
		except:
 		    pass
 		
 		time.sleep(2)
 			
 		winHandlep=self.driver.window_handles
 		self.driver.switch_to_window(winHandlep[-1])
 		
 		self.collect_product()
 		
 		winHandlepro=self.driver.window_handles
 		self.driver.switch_to_window(winHandlepro[-1])
 		self.driver.close()
		
		
		
		
 	def collect_product(self):
 		if self.es(".tb-key .tb-sku .tb-prop") is not None:
 			try:
	 			property=self.es(".tb-key .tb-sku .tb-prop")
				for l in property:
					item=l.es("li a span")[0]
					item.click()
					time.sleep(1)
			except:
				pass
		else:
			pass
		
		try:
	 		collect_bar=self.e("#J_LinkBasket")
			collect_bar.click()
			self.client.screenshot_as_file("put_bart_ok.png")
			time.sleep(1)
		except:
			pass
		
		try:
			
			get_product=self.e("#J_Favorite")
			get_product.click()
			time.sleep(1)
			self.client.screenshot_as_file("store_product_ok.png")
		except:
			pass
		
		self.driver.close()
	

	
	def e(self, l):
	    return self.client.e(l)
	
	def es(self, l):
	    return self.client.es(l)
			
			
       
        
