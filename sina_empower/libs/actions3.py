#-*- coding: utf8 -*-
from __future__ import with_statement
from contextlib import closing

import sys
import time,os
import logging
import TaodianApi

class SendConpon(object):
    def __init__(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        
        self.logger = logging.getLogger("grab.log")
        
        self.DATA={}
        self.fans=[]
        pass
    def __call__(self, client, api, url='', **kw):
      
         self.client = client
         
         self.wb_name = kw['login_user']
         self.wb_passwd = kw['login_passwd']
         self.account=kw['wb_account']
         self.driver = client.driver
         self.api = api
         driver = self.driver
         
         self.logger.info("====================current account:%s=====================" % self.account)
         self.open_weibo()
         self.client.driver.implicitly_wait(2)
             
         for i in range(2):
             if self.e("#pl_content_top .gn_name") is not None:
                 self.start_search()
                 imData=self.get_fans()
                 
                 if imData is False:
                     return
                 else:
                     pass
                 
#                  self.export_fans(imData, api)
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
#         try:
            searchInput=self.e("#pl_content_top .gn_search .gn_input")
            searchInput.send_keys(self.account)
            time.sleep(1)
            
            submitInput=self.e("#pl_content_top .gn_search .gn_btn")
            submitInput.click()
            
            time.sleep(2)
            self.logger.info("find wb_account:%s" % self.account)
#         except:
#             self.logger.info("not go to search....")
          
    def get_fans(self):
               
        winHandleBefore=self.driver.current_window_handle
        
        weiBtn = self.e("#pl_weibo_direct")
        try:
            if weiBtn.e(".person_num") is not None:
                fanButton = weiBtn.es(".person_num span a")[1]
            else:
                fanButton = weiBtn.es(".star_num span a")[1]
                
            fanButton.click()
        except:
            self.logger.info("can not find fans button successly")
            return False

        time.sleep(2)
        
        for winHandle in self.driver.window_handles:
            if winHandle==winHandleBefore:
                continue
            self.driver.switch_to_window(winHandle)
           
        cur_url=self.driver.current_url
        
        cur_account=cur_url[cur_url.find('weibo.com')+10:]
        account_id=cur_account[:cur_account.find('/')]
        
        try:
            int(account_id)
            pass
        except ValueError:
            return False

        
        
        self.find_page_fans(account_id)
        
        nextBtn=self.e(".W_pages .W_btn_c span")
        while True:
            
            if nextBtn is not None:
                try:
                  nextBtn.click()
                except:
                  self.logger.info('can not get more fans')
                  break
                time.sleep(2)
                self.find_page_fans(account_id)
                
            else:
                break
            
            try:
                nextBtn=self.es(".W_pages .W_btn_c span")[1]
            except:
                self.logger.info('current page is the last page')
                break

#         self.driver.close()
#         self.driver.switch_to_window(winHandleBefore)
#         self.driver.close()
#          
#         self.DATA={'out_id':account_id,'fans':self.fans}
       
        return True         
     
    def export_fans(self, imData, api):
        api = TaodianApi.TaodianApi()
        param = {"out_id" : imData['out_id'] , "data": imData['fans']}
        rs = api.call("fans_import_fans_data", param)
        
        param2 = {"nick" : self.account}             
      
        if(rs["status"] == "ok"):
            rs2 = api.call("fans_scan_plan_updata", param2)
            self.logger.info("import fans status is ok")
        else:
            self.logger.info("import fans status is error")
          
        
           
    def find_page_fans(self,account_id):
        try:
            allfans=self.es(".cnfList li")
        
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
                
                if int(follow_count)>1000:
                    continue
                if int(fans_count)>10000:
                    continue
                
                
                detail=uid+";"+nick+";"+face+";"+sex+";;;"+province+";"+fans_count+";"+follow_count+";"+wb_count
                self.logger.info("fans: %s" % detail)
#                 self.fans.append(detail)
                self.fans=[detail]

                self.DATA={'out_id':account_id,'fans':self.fans}
                
                self.export_fans(self.DATA, self.api)
                
                
 
        except:
             self.logger.info("can not find fans detail successly")
#             
            
    def e(self, l):
        return self.client.e(l)
    
    def es(self, l):
        return self.client.es(l)