# -*- coding: utf8 -*-

import logging
import os
import urllib2
import urllib
import re
import time
import traceback 
import threading
import random

class getImgsByHtml(object):
	def __init__(self, ):
		self.logger = logging.getLogger("click")
	def __call__(self, client, api, **kw):
		
		self.file_dir = ''
		self.url = kw['url']
		
		self.getPath()
		
		self.getImgProxy()
		
		self.getHtml()
		self.getImg()
		
	def getImgProxy(self):
	
		self.targets = []
		self.rawProxyList = []
		self.checkedProxyList = []
		
		self.getTarget()
		self.getProxy()
		self.checkProxy()
		
		
	def getTarget(self):
	
		for i in xrange(1,9):
	        target = r"http://www.cnproxy.com/proxy%d.html" % i
	        self.targets.append(target)
		
	def getProxy(self):
		req = urllib2.urlopen(self.target)
        result = req.read()
        
        p = re.compile(r'''<tr><td>(.+?)<SCRIPT type=text/javascript>document.write\(":"\+(.+?)\)</SCRIPT></td><td>(.+?)</td><td>.+?</td><td>(.+?)</td></tr>''')
        matchs = p.findall(result)
        
        for row in matchs:
            ip=row[0]
            port =row[1]
            port = map(lambda x:portdicts[x],port.split('+'))
            port = ''.join(port)
            agent = row[2]
            addr = row[3].decode("cp936").encode("utf-8")
            proxy = [ip,port,addr]

            self.rawProxyList.append(proxy)
		
	def checkProxy(self):
		cookies = urllib2.HTTPCookieProcessor()
		
        for proxy in self.rawProxyList:
            proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(proxy[0],proxy[1])})
            
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')] 

            t1 = time.time()

            try:
                req = opener.open("http://www.baidu.com/", 5)
                result = req.read()

                timeused = time.time() - t1
                pos = result.find("030173")

                if pos > 1:
                    checkedProxyList.append((proxy[0],proxy[1],proxy[2],timeused))
                else:
                     continue
            except Exception,e:
                continue	
		
	

	def getHtml(self):
		import socket
		timeout = 20
		socket.setdefaulttimeout(timeout)
		sleep_download_time = 20
		
		try:  
			time.sleep(sleep_download_time)
			page = urllib.urlopen(self.url)
			html = page.read()
			self.html = html
			page.close()  
		      
		except UnicodeDecodeError as e:  
		         
		    print('-----UnicodeDecodeError url:',self.url)  
		      
		except urllib.error.URLError as e:  
		    print("-----urlError url:",self.url)  
		  
		except socket.timeout as e:  
		    print("-----socket timout:",self.url)  			
		
	def getPath(self):

		curr_path = os.getcwd()
		curr_path = curr_path.replace('\\', '/')
		self.file_dir = curr_path + '/'+ 'uploads' + '/'
		if os.path.exists(self.file_dir) is False:  
			os.mkdir(self.file_dir)
 
	def getImg(self):
		
		img=re.compile(r"""<img\s.*?\s?src\s*=\s*['|"]?([^\s'"]+).*?>""",re.I)
		imglist = img.findall(self.html) 
				
		for imgurl in imglist:
		
			x = int(time.time())
			type = '%s.jpg' % x  
			filepath = self.file_dir + type
			
			cookies = urllib2.HTTPCookieProcessor()
            randomCheckedProxy = random.choice(self.checkedProxyList) 
            proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(randomCheckedProxy[0],randomCheckedProxy[1])})
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
            urllib2.install_opener(opener)

			
			if imgurl.startswith('http') or imgurl.startswith('https') is True:
				self.logger.info("--------start download img: %s, source url: %s----------"  %(type,imgurl))
				try:
					urllib.urlretrieve(imgurl,filepath)
					self.logger.info("-------success download img: %s, done!--------------"  %(type))
				except Exception, e:
					self.logger.info("-------exception: %s, detail info: %s" %(e,traceback.format_exc()) )
					self.logger.info("-------falied download img: %s" %(type) )
			else:
				pass
			
	def getImgTest(self):

		imgurl="http://mgt.21451.com/doc/public/pt_1102/2014-01-26/1389496683369.jpg"
		filepath = os.getcwd() + '/' + '1.jpg'
		urllib.urlretrieve(imgurl,filepath)

	 
	