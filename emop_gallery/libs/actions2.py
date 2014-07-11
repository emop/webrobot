# -*- coding: utf8 -*-

import logging
import re
import os
import urllib2
import urllib
import traceback 
import threading
import time
import random
import socket		

class getImgsByElement(object):
	def __init__(self, ):
		self.logger = logging.getLogger("click")
	def __call__(self, client, api, **kw):
		
		self.client = client
		self.driver = self.client.driver
		self.file_dir = ''
		
		self.ProxyList = []
		self.checkedProxyList = []
		
		self.url = kw['url']
		self.dir = kw['dir']
		

		self.getPath()		
		self.getImg()
		self.driver.close()

	
		
		
	def getPath(self):

		curr_path = os.getcwd()
		curr_path = curr_path.replace('\\', '/')
		self.file_dir = curr_path + '/'+ 'uploads' + '/'
		
		if self.dir:
		    self.file_dir = self.file_dir + self.dir + '/'
		
		if os.path.exists(self.file_dir) is False:  
			os.mkdir(self.file_dir)
 
	def getImg(self):
		self.driver.get(self.url)
		time.sleep(5)	
		
		imglist=self.client.es('img')

		for img in imglist:
		
			imgurl = self.driver.execute_script('return arguments[0].getAttribute("src")',img)
			time.sleep(1)			
		
			x = int(time.time())
			type = '%s.jpg' % x  
			filepath = self.file_dir + type
			
			socket.setdefaulttimeout(300)
			
			if imgurl.startswith('http') or imgurl.startswith('https') is True:
				self.logger.info("--------start download img: %s, source url: %s----------"  %(type,imgurl))
				try:
					urllib.urlretrieve(imgurl,filepath)
					self.logger.info("-------success download img: %s, --------------"  %(type))
				except Exception, e:
					self.logger.info("-------exception: %s, detail info: %s" %(e,traceback.format_exc()) )
					self.logger.info("-------falied download img: %s" %(type) )
			else:
				pass
	
	
	
	
	
	
	
	
	def getProxy(self,):
	
		portdicts ={'v':"3",'m':"4",'a':"2",'l':"9",'q':"0",'b':"5",'i':"7",'w':"6",'r':"8",'c':"1"}
	
		for i in xrange(1,10):
			target = r"http://www.cnproxy.com/proxy%d.html" % i
			req = urllib2.urlopen(target)
			
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
	
	            self.ProxyList.append(proxy)
	    
		print self.ProxyList
		self.checkProxy()	
		
	def checkProxy(self):
			cookies = urllib2.HTTPCookieProcessor()
			
			import socket
			socket.setdefaulttimeout(30)
			
			for proxy in self.ProxyList:
			    proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(proxy[0],proxy[1])})
			    
			    print r'http://%s:%s' %(proxy[0],proxy[1])
			    
			    opener = urllib2.build_opener(cookies,proxyHandler)
			    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')] 
			     			
			    t1 = time.time()
			
			    try:
			        req = opener.open("http://www.baidu.com/", 30)
			        result = req.read()
			
			        timeused = time.time() - t1
			        print result
			        pos = result.find("030173")
			        print pos
			
			        if pos > 0:
			            self.checkedProxyList.append((proxy[0],proxy[1],proxy[2],timeused))
			        else:
			             continue
			    except Exception,e:
			        continue	

	
	

	def getImgTest(self):

		import socket
		socket.setdefaulttimeout(30)
		
		cookies = urllib2.HTTPCookieProcessor()
		randomCheckedProxy = random.choice(self.checkedProxyList) 
		proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(randomCheckedProxy[0],randomCheckedProxy[1])})
		opener = urllib2.build_opener(cookies,proxyHandler)
		opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0')]
		urllib2.install_opener(opener)


		imgurl="http://mmbiz.qpic.cn/mmbiz/fbqIW6MeBu5hU8xoKzGuIyAY9rlhxib8kK2SUQ33ZObVWNibGOE8odLjMtLaVibtbUzEwzP3NMKjWrRjEmf2VwHqA/0"
		filepath = os.getcwd() + '/' + '1.jpg'
		urllib.urlretrieve(imgurl,filepath)
