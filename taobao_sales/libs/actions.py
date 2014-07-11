# -*- coding: utf8 -*-
import sys
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
		self.logger.info("============ start for sales of %s ============" % kw['commodity_id'])
		taobao = "http://item.taobao.com/item.htm?id="
		commodity_url = taobao + kw['commodity_id']
		
		self.logger.info("open the url: %s" % commodity_url)
		the_url = self.open_commodity_url(client, commodity_url)
		self.logger.info("current url after load item:%s" % the_url)
			
		try:
			sales = self.get_sales_by_url(client, the_url, kw['commodity_id'])
		except Exception, e:
			self.logger.exception(e)
			file_name = kw['commodity_id'] + ".png"
			client.screenshot_as_file(file_name)
			sales = "0"
		finally:
			data = {}
			data['num_iid'] = kw['commodity_id']
			data['sales'] = sales
			self.logger.info("updata %s sales :%s" %(data['num_iid'], data['sales']))
			msg = api.http.post_data("http://emopshop.sinaapp.com/Sales/updata_Commodity_sales", data)
			msa = api.http.post_data("http://7.emop.sinaapp.com/WeiboHotUpdata/sync_salse_to_weibolib", data)
			self.logger.info("updata Result:%s" % msg)
			self.logger.info("emop updata Result:%s" % msa)
			
			self.logger.info("============ end for sales of %s ============" % kw['commodity_id'])
		
	def open_commodity_url(self, client, url):
		try:
			client.driver.get(url)
			time.sleep(3)
		except:
			self.logger.warn("the page time out")
			
		return client.driver.current_url
	
	def get_sales_by_url(self, client, the_url, commodity):
		the_taobao = "http://item.taobao.com/item.htm"
		the_tianmao = "http://detail.tmall.com/item.htm"
		sales = None;
		
		if the_url.find(the_taobao) == 0:
			client.driver.switch_to_default_content()
			#client.screenshot_as_file("0001.png")
			sales = client.e(".tb-sold-out .J_TDealCount").text
			if sales == "":
				xx = client.e(".tb-sold-out .J_TDealCount")
				new = client.driver.execute_script(
			    "arguments[0].style[\"display\"] = \"block\";"+
			    "arguments[0].style[\"visibility\"] = \"visible\";"+
			    "return arguments[0];", 
			    xx.element)				
				sales = new.text
				self.logger.info("try to change the element to visiable and get sales:%s" % sales)
				
				file_name = commodity + ".png"
				self.logger.info("the file name :%s" %file_name)
				client.screenshot_as_file(file_name)
			else:
				self.logger.info("the %s sales is : %s" %(commodity,sales) )
		elif the_url.find(the_tianmao) == 0:
			sales = client.e(".tb-sold-out .J_TDealCount").text
			if sales == "":
				self.logger.info("the %s is an expired commodity" % commodity)
				file_name = commodity + ".png"
				client.screenshot_as_file(file_name)
				
				xx = client.e(".tb-sold-out .J_TDealCount")
				new = client.driver.execute_script(
			    "arguments[0].style[\"display\"] = \"block\";"+
			    "arguments[0].style[\"visibility\"] = \"visible\";"+
			    "return arguments[0];", 
			    xx.element)				
				sales = new.text	
				self.logger.info("try to change the element to visiable and get sales:%s" % sales)			
			else:
				self.logger.info("the %s sales is : %s" %(commodity,sales) )
		else:
			self.logger.info("undefind the %s ")
			file_name = commodity + ".png"
			client.screenshot_as_file(file_name)
			sales = "0"
		return sales
		
		"""   
			def get_sales_by_url_2(self, client, the_url):
		try:
			sales = client.e(".tb-sold-out .J_OrdersPaid").text
			if sales == "":
				print "sales is undefind"
			self.logger.info("this is taobao's commodity, the salse is %s" % sales)
		except:
			try:
				sales = client.e(".tb-sold-out .J_TDealCount").text
				self.logger.info("this is tianmao's commodity, the salse is %s" % sales)
			except:
				sales = "0"
				self.logger.info("the commodity no found")
		return sales
		 """
