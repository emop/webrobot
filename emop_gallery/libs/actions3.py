# -*- coding: utf8 -*-

import logging
import os
import time


class saveImgsToUpyun(object):
	def __init__(self, ):
		self.logger = logging.getLogger("click")
	def __call__(self, client, api, **kw):
		
		self.bucketName = 'mobile01'
		self.userName = 'sae'
		self.passWord = 'taodian401'
		self.count = 0
		
		self.saveImg(api)
		

	def saveImg(self,api):
	
		from sailing import upyun
		up = upyun.UpYun(self.bucketName,self.userName,self.passWord,timeout=30,endpoint=upyun.ED_AUTO)
		
		print("==================================================")
		print("Getting Started with UpYun Storage Service")
		print("==================================================\n")
		
		rootpath = '/emopcrm/'
		
		try:
			res = None
			print("Uploading a new object to UpYun from a file ...")
			
			headers = {}
			
			
			file_dir = self.getFileDir()
			list = os.listdir(file_dir)	
			
			for line in list:
				time.sleep(1)
				with open(file_dir+'/'+line, 'rb') as f:
					x = int(time.time())
					type = '%s.jpg' % x 
					pic_path = rootpath + type
					res = up.put(pic_path, f, checksum=False,headers=headers)	
						
				ispicbucket = True
				if res:
					pic_url = 'http://'+self.bucketName+'.b0.upaiyun.com'+pic_path
					self.logger.info("start upload to sql for img: %s" % (pic_url))
					data = {'pic_url':pic_url}
					self.saveImgToSQL(data,api)
				else:
				    ispicbucket = False   
	            
		except upyun.UpYunServiceException as se:
			print("failed\n")
			print("Except an UpYunServiceException ...")
			print("HTTP Status Code: " + str(se.status))
			print("Error Message:    " + se.msg + "\n")
			if se.err:
			    print(se.err)
		except upyun.UpYunClientException as ce:
			print("failed\n")
			print("Except an UpYunClientException ...")
			print("Error Message: " + ce.msg + "\n")
			
			
		self.logger.info("the count of all Image: %s" % (self.count))	
		
			
	def getFileDir(self):
	
		curr_path = os.getcwd()
		curr_path = curr_path.replace('\\', '/')
		
		file_dir = curr_path + '/'+ 'uploads' + '/short'
		return file_dir


		
		
	def saveImgToSQL(self,data,api):
		
		resp = api.http.post_data("http://emopcrm.sinaapp.com/queue/syns_pic_to_gallery", data)
		
		if resp == 'ok':
			self.count = self.count+1
		
		self.logger.info("end for response:%s" % (resp))
		
		return resp


	 
	