#-*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import sys
import time
import logging

class SendConpon(object):
    def __init__(self):
         self.logger = logging.getLogger("try")
         
         pass
    def __call__(self, client, api, url='', **kw):
         self.client = client
         try:
                     client.driver.get('http://try.taobao.com/item.htm?spm=a1z0i.1000798.1000585.4.Nn1GuK&id=6278854&qq-pf-to=pcqq.c2c')
                     time.sleep(1)
                     
         except Exception, e:
                     self.logger.exception("!!!!!!!Failed to open complete url !!!!!!!!:%s" % e)
        
         
         
#          trydetailBtn = self.e("#J_Tab ul li span")
#          print trydetailBtn
#          trydetailBtn.click()
#          time.sleep(1)
         
         self.findRow()
         while True:
             if self.e("a.next-page") is not None:
                 current = self.e("span.current").text
                 try:
                     self.e("a.next-page").click()
                     time.sleep(1)
                     self.findRow()
                 except:
                     self.logger.info("falied get:%s" %current)
             else:
                 break
         
            
    def findRow(self):
         conpons = self.es(".apply-detail .items .apply-item")
         
         for row in conpons:
             print "row:%s"  % row.text
             if row.e(".nick") is not None:
                 n=row.e(".nick").text
                 self.putContent(n)
                 
             else:
                 continue
      
    def putContent(self, n):
        from sailing.core import RowTask
        
        task = RowTask("test.csv","ww.csv")
        writer = task._get_done_writer()
        writer.write("%s\n" % n)
        self.logger.info("try:%s" % n)   
        
    def e(self, l):
        return self.client.e(l)
    
    def es(self, l):
        return self.client.es(l)
        
   

             
        
       
        
