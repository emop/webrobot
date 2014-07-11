#-*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import sys
import time,os
import logging

class SendConpon(object):
    def __init__(self):
         self.logger = logging.getLogger("grab")
         self.DATA={}
         pass
    def __call__(self, client, api, url='', **kw):
      
         self.client = client
         
         self.wb_name = '452664116@qq.com'
         self.wb_passwd = 'zhouli78'
         self.account=kw['wb_account']
         self.driver = client.driver
         driver = self.driver
         
         
         self.open_weibo()
         self.client.driver.implicitly_wait(2)
             
         for i in range(2):
             if self.e("#pl_content_top .gn_name") is not None:
                 self.start_search()
                 fans=self.get_fans()
                 self.export_fans(fans, api)
                 break
             else:
                 self.login_wb()
             
                 
             
         
    def open_weibo(self):
        
        self.client.driver.implicitly_wait(5)
        self.client.driver.get("http://www.weibo.com")
        time.sleep(1)
        
    def login_wb(self):
        
        self.logger.info("start user with wb loging...")
        try:
            nameInput=self.e("#pl_login_form .username .W_input ")
            nameInput.send_keys(self.wb_name)
            
            passdInput=self.e("#pl_login_form .password .W_input")
            passdInput.send_keys(self.wb_passwd)
            time.sleep(1)
            
            submitInput=self.e("#pl_login_form .login_btn span")
            submitInput.click()
            time.sleep(2)
            
        except:
            self.logger.info("not success login wb....")
            

        
    def start_search(self):
        try:
            searchInput=self.e("#pl_content_top .gn_search .gn_input")
            searchInput.send_keys(self.account)
            time.sleep(1)
            
            submitInput=self.e("#pl_content_top .gn_search .gn_btn")
            submitInput.click()
            
            time.sleep(1)
            self.logger.info("find wb_account:%s" % self.account)
        except:
            self.logger.info("not go to search....")
          
    def get_fans(self):
               
        winHandleBefore=self.driver.current_window_handle
        
        fanButton=self.es("#pl_weibo_direct .person_num span a")[1]
        fanButton.click()
        time.sleep(2)
        
        for winHandle in self.driver.window_handles:
            if winHandle==winHandleBefore:
                continue
            self.driver.switch_to_window(winHandle)
            
        self.find_page_fans()
        
        nextBtn=self.e("#Pl_Official_LeftHisRelation__38 .W_pages .W_btn_c span")
        while True:
            
            if nextBtn is not None:
                try:
                  nextBtn.click()
                except:
                  self.logger.info('can not get more fans')
                  break
                time.sleep(2)
                self.find_page_fans()
                
            else:
                break
            nextBtn=self.es("#Pl_Official_LeftHisRelation__38 .W_pages .W_btn_c span")[1]
            
        self.driver.close() 
        print self.DATA.keys()  
        return self.DATA          
     
    def export_fans(self, fans, api):
        self.logger.info("start to export fans to api")
        resp = api.http.post_data("http://web.emop.cn/queue/fans_import_fans_data", fans)
        
        self.logger.info("emop response:%s" % resp)
          
        
           
    def find_page_fans(self):
        try:
            allfans=self.es("#Pl_Official_LeftHisRelation__38 .cnfList li")
        
            for row in allfans:
                
                strArr=self.driver.execute_script('return arguments[0].getAttribute("action-data")',row)
                strArr_uid=strArr[:strArr.find('&')]
                
                uid=strArr_uid[strArr_uid.find('=')+1:]
                sex=strArr[-1:]
                
                imgNode=row.e(".left .face a img")
                face=self.driver.execute_script('return arguments[0].src',imgNode)
                nick=row.e(".con .con_left .name a").text
                province=row.e(".con .con_left .name .addr").text
                
                follow_count=row.es(".con .con_left .connect a")[0].text
                fans_count=row.es(".con .con_left .connect a")[1].text
                wb_count=row.es(".con .con_left .connect a")[2].text
                
                detail={'uid':uid,
                            'sex':sex.encode("utf8"),
                            'face':face,
                            'province':province.encode("utf8"),
                            'follow_count':follow_count,
                            'wb_count':wb_count,
                            'fans_count':fans_count
                            }
                newDic={uid:detail}
            
                self.DATA.update(newDic)
 
        except:
             self.logger.info("can not find fans detail successly")
#             
            
    def e(self, l):
        return self.client.e(l)
    
    def es(self, l):
        return self.client.es(l)