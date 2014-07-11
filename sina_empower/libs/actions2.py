# -*- coding: utf8 -*-
import os
import sys
import time
import logging
import urllib2
import re
import signal
import TaodianApi

class SinaSmsActivate(object):
	def __init__(self, ):
		self.logger = logging.getLogger("click")
		
	def __call__(self, client, api, **kw):
		"""
		client -- 
		client
		api --        
		"""
		self.api = api
		username = kw['login_user']
		pw = kw['login_password']
		self.out_id = kw['out_id']
		self.platform = kw['platform']
		#self.login_feiq()
		file_name = username + "png"
		
		url = "http://www.weibo.com"
		#signal.signal(signal.SIGINT, signal_handler)
		self.logger.info("==============start : %s  ==============" % username)
		fd = urllib2.urlopen("http://192.168.3.200:8090/switch_ip")
		self.logger.info("switch ip:" + fd.read())
		fd.close()
		
		cur_url = self.open_url(client, url)
		self.logger.info("current url :%s" % cur_url)
		
		lg = self.login_weibo(client, username, pw)
		if lg:
			try:
				rs = self.sms_activate(client , file_name)
				if rs :
					self.weibo_account_update()
				else:
					pass
			except:
				self.cance_all(client)
		else:
			self.logger.error("Sign encountered an error")
		self.cance_all(client)
		self.logger.info("==============end : %s  ==============" % username)
		
	def open_url(self, client, sina_url):
		try:
			self.logger.info("start open the sina host page :%s" % sina_url)
			client.driver.get(sina_url)
			time.sleep(3)
		except:
			self.logger.warning("open the sina host timeout")
		return client.driver.current_url
			
	def login_weibo(self, client, username, pw):
		the_element = ""
		self.logger.info("start login the  weibo")
		try:
			the_element = client.e(".username .W_input")
		except:
			self.logger.error("not found the username element")
			return False
		the_element.send_keys(username)
		self.logger.info("input the username : %s" % username )
		time.sleep(1)
			
		try:
			the_element = client.e(".password .W_input")
		except:
			self.logger.error("not found the password element")
			return False
		the_element.send_keys(pw)
		self.logger.info("input the password : %s" % pw )
		time.sleep(1)
		
		try:
			the_element = client.e('.login_btn .W_btn_g')
		except:
			self.logger.error("not found the login_btn element")
			return False
		the_element.click()
		self.logger.info("click the login button, please wait 5 seconds" )
		time.sleep(5)
		
		return True


	def sms_activate(self, client, file_name):
		cur_url = client.driver.current_url
		captcha_code = ""
		phone_num = ""
		the_element = ""
		if(cur_url == "http://sass.weibo.com/unfreeze"):
			self.logger.info("start sms_activate  weibo")
			try:
				the_element = client.e(".phone .W_input input")
			except:
				self.logger.error("not found the input phone element")
				return False
			phone_num = self.get_phone_num()
			if phone_num['status'] == "error":
				self.logger.error("Server is busy, there is no number")
				return False
				
			the_element.send_keys(phone_num['phone_num'])
			self.logger.info("input the phone code : %s" % phone_num['phone_num'] )
			time.sleep(1)
			
			
				
			try:
				the_element = client.e(".phone .W_btn_b")
			except:
				self.logger.error("not found the sms send button element")
				return False
			the_element.click()
			self.logger.info("Click the Send sms button, you will see a messagebox" )
			
			time.sleep(2)
			
			try:
				the_element = client.e(".W_layer .W_texta")
			except:
				return False
			self.logger.info("the messagebox : %s" % the_element.text)
			mbx = the_element.text.encode("utf8")
			msg = "验证码已经发送到您的手机"
			#msg = msg.decode('utf8')
			#msg.decode('utf8')
			if mbx.find(msg) < 0 :
				#self.logger.info("message index of : %s" % the_element.text.find(msg)
				return
			
			client.screenshot_as_file(file_name)
			
			try:
				the_element = client.e(".W_layer .W_btn_b")
			except:
				self.logger.error("not found the messagebox Confirm button element")
				return False
			the_element.click()
			self.logger.info("click the messagebox Confirm button , please wait 30 seconds" )
			time.sleep(30)
			
				
			try:
				the_element = client.e(".verification input")
			except:
				self.logger.error("not found the input captcha element")
				return False
			captcha_code = self.get_captcha_code(phone_num['phone_num'])
			if captcha_code['status'] == "error":
				self.logger.error("Get captcha code fails")
				return False
			the_element.send_keys(captcha_code['captcha_code'])
			self.logger.info("input the captcha code : %s" % captcha_code['captcha_code'])
			time.sleep(1)
			
				
			try:
				the_element = client.e(".submit_button .W_btn_b")
			except:
				self.logger.error("not found the confirm button element")
				return False
			the_element.click()
			self.logger.info("Click the confirm button to complete the action")
		else:
			self.logger.error("Activation is not required")
			return True
		return True
			
	def weibo_account_update(self):
		api = TaodianApi.TaodianApi()
		param = {"out_id" : self.out_id , "platform": self.platform , "user_status": "ok"}
		rs = api.call("timing_weibo_account_update", param)
		#self.logger.info("the message: %s" % rs)
		if(rs["status"] == "ok"):
			self.logger.info("weibo_account_update is ok")
		else:
			self.logger.info("weibo_account_update is error")
		
	def login_feiq(self):
		login_str = "action=loginIn&uid=woyastar&pwd=xingkong"
		login_code = self.api.http.post_data("http://sms.xudan123.com/do.aspx", login_str)
		self.logger.info("the login_code : %s " % login_code)
	
	def get_captcha_code(self, phone_num):
		captcha_str = "action=getVcodeAndReleaseMobile&mobile="+ phone_num +"&token=2f4ef58d4314dfd6f6052075fd375447&uid=woyastar"
		cancel_str = "action=cancelSMSRecv&mobile="+ phone_num +"&token=2f4ef58d4314dfd6f6052075fd375447&uid=woyastar"
		captcha_code = "not_receive"
		data = {'status':"error", 'captcha_code':"no_data"}
		for i in range(31):
			captcha_code = phone_num = self.api.http.post_data("http://sms.xudan123.com/do.aspx", captcha_str)
			self.logger.info("try get captcha_code : %s th , the chptcha_code str:%s" % (i, captcha_code))
			if captcha_code != "not_receive":
				captcha_code = re.findall(r'\[(.*)\]', captcha_code)
				data['status'] = "ok"
				data['captcha_code'] = captcha_code
				break
			if i ==30:
				cancel_code = self.api.http.post_data("http://sms.xudan123.com/do.aspx", cancel_str)
				self.logger.info("cancel get captcha code return : %s" % cancel_code)
			time.sleep(10)
		return data
	
	def get_phone_num(self):
		phone_str = "action=getMobilenum&pid=48&uid=woyastar&token=2f4ef58d4314dfd6f6052075fd375447"
		data = {'status':"error", 'phone_num':"no_data"}
		phone_num = "no_data";
		for h in range(5):
			for i in range(15):
				phone_num = self.api.http.post_data("http://sms.xudan123.com/do.aspx", phone_str)
				self.logger.info("try get phone_num : %s th , the phone_num str:%s" % (i, phone_num))
				if phone_num != "no_data":
					phone_num = phone_num.split("|")
					#phone_num = phone_num[0]
					data['status'] = "ok"
					data['phone_num'] = phone_num[0]
					break
				time.sleep(1)
			if data['status'] == "ok" :
				break
		return data
	def cance_all(self,client):
		cance_all = "action=cancelSMSRecvAll&uid=woyastar&token=2f4ef58d4314dfd6f6052075fd375447"
		cancel_code = self.api.http.post_data("http://sms.xudan123.com/do.aspx", cance_all)
		self.logger.info("Release resources")
		client.driver.close()
		
	def signal_handler(signal, frame):
		self.cance_all()
