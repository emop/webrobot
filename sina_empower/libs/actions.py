# -*- coding: utf8 -*-
import os
import sys
import time
import logging
import urllib2

class SinaBatchEmpower(object):
	def __init__(self, ):
		self.logger = logging.getLogger("click")
		
	def __call__(self, client, api, **kw):
		"""
		client -- 
		client
		api --        
		"""
		
		self.logger.info("============ start for sales  ============")
		fd = urllib2.urlopen("http://192.168.3.200:8090/switch_ip")
		self.logger.info("switch ip:" + fd.read())
		fd.close()
		
		self.client = client
		self.driver = client.driver
		#tid = kw['tid']
		tid = client.client_id
		username = kw['login_user']
		pw = kw['login_password']
		url = "http://www.zaol.cn/weibo/login.php?tid="+tid
		#self.logger.info("============ start for sales  ============")
		
		path=os.getcwd()
		self.logger.info("the path :%s" % path)
		self.logger.info('tid : %s  username: %s     password:%s  url:%s' %(tid, username, pw, url))
		self.open_empower_url(url)
		self.sina_empower(client, username, pw)
		self.logger.info("============ end for sales ============")
	
	def open_empower_url(self, url):
		self.logger.info("start open: %s" %(url))
		self.client.driver.get(url)
		#time.sleep(1)
		
	def sina_empower(self, client, username, pw):
		userid = client.e("#userId")
		userid.send_keys(username)
		time.sleep(1)
		
		passwd = client.e("#passwd")
		passwd.send_keys(pw)
		time.sleep(1)
		
		self.logger.info(" first click the submit ")
		submit = client.e(".WB_btn_login.formbtn_01")
		submit.click()
		time.sleep(1)

		#codeinput = client.e(".WB_iptxt.oauth_form_input.oauth_form_code")
		i=0;
		for i in range(3):
			#while (client.e(".oauth_form_code") is not None) and (i<5):
			client.driver.switch_to_default_content()
			codeinput = client.e(".oauth_form_code")
			if codeinput is None: break
			i=i+1
			try:
				self.logger.info("start get input captcha code.")
				
				full_screen_path = client.real_path("screen.png")
				captcha_path = client.real_path("captcha.png")
				self.logger.info("the img is save")
				#for i in range(3):
				code = self._get_captcha_code(client.driver,{'x':0,'y':0},full_screen_path, captcha_path)

				if code is None:
					break
				#codeinput = client.e(".oauth_form_code")
				codeinput.clear()
				codeinput.send_keys(code)
				
				submit = client.e(".WB_btn_login.formbtn_01")
				submit.click()
				time.sleep(3)
			except:
				pass
		
		client.screenshot_as_file("after_input_captcha_code.png")
		client.driver.switch_to_default_content()
		connect = client.e(".oauth_login_submit .formbtn_01")
		if connect is not None:
			connect.click()
			time.sleep(1)
		client.screenshot_as_file("login_done.png")

		client.close()
		
	def _get_captcha_code(self, driver, p, full_screen_path, captcha_path):
		self.logger.info("the screen path: %s" % full_screen_path)
		driver.get_screenshot_as_file(full_screen_path)	
		
		try:
			verifyshow = driver.find_element_by_css_selector(".code_img")
		except:
			self.logger.info("Not found vrify code")
			return None
		vp = verifyshow.location
		s = verifyshow.size
		
		#box = (left, top, left+width, top+height)
		left = p['x'] + vp ['x']
		top = p['y'] + vp['y']
		new_box = (int(left), int(top), int(left + s['width']), int(top + s['height']))
			
		self.save_screenshot_img(full_screen_path, captcha_path, new_box)
		
		from sailing.webrobot.captcha import get_captcha

		self.logger.info("starting get captcha: %s" % (captcha_path, ))		
		#data = self._get_code_hao(captcha_path)
		data = get_captcha(captcha_path, )
		self.logger.info("captcha response:%s" % str(data))
	
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
		
		fd = open(out_path, 'rb')
		data = fd.read()
		#print "image data size:%s, path:%s" % (len(data), out_path)
		#print "image data:%s" % str(data)
		#img.close()
		pass

