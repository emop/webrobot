# -*- coding: utf8 -*-
import logging
import time
import hashlib
import urllib2
import json
import urllib

class TaodianApi:
	appkey = "63"
	appSecret = "c8bdecf1d3778e3a463475290886aa58"
	apiUrl = "http://api2.zaol.cn/api/route"
	def __init__(self):
		self.logger = logging.getLogger("click")
		
		self.logger.info("the logger test")
		try:
			setting = open("TaodianApi.conf","r")
			try:
				line = setting.readline()
				while line:
					data = line.split("=", 1)
					if data[0] == "td_api_id":
						self.appkey = data[1]
						self.logger.info("the appkey:%s" % self.appkey)
					if data[0] == "td_api_secret":
						self.appSecret = data[1]
					line = setting.readline()
			except:
				self.logger.info("read file error")
			finally:
				setting.close()
		except:
			self.logger.info("no found 'TaodianApi.conf'")
	
	def call(self, api, param):
		p = self.getSign()
		p["name"] = api
		p["params"] = json.dumps(param)
		fd = urllib2.urlopen(self.apiUrl,data = urllib.urlencode(p))
		result = fd.read()
		fd.close()
		
		return json.loads(result)
		
		
		
	def getSign(self):
		
		stamp = time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))
		signStr = self.appkey +","+ stamp +","+self.appSecret
		
		sign = hashlib.md5(signStr).hexdigest()
		
		p = {"app_id":self.appkey, "time":stamp, "sign":sign}
		
		return p
		


