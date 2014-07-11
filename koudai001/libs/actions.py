from taobao import Taobao
from oss.oss_xml_handler import *
from oss.oss_api import *
from sailing.common.common import *
import re
from time import localtime, strftime, sleep
import logging
import json
import os

class GetTaokDetail(object):
    def __init__(self, ):
        self.logger = logging.getLogger("taoke")
        
    def __call__(self, site, http, next_task, url, local_url, *args):
        num_iid = re.search(r"/(\d{7,})/", url).group(1)
        self.logger.info("start fetch taoke details id:%s" % num_iid)
    
        if os.environ.get('HUDSON_URL'):
            http.post_data("http://127.0.0.1:8924/queue/q/waiting_import?format=json", {'num_iid': num_iid, 'detail_url':url}, {})
        else:
            http.post_data("http://data.deonwu84.com/queue/q/waiting_import?format=json", {'num_iid': num_iid, 'detail_url':url}, {})
        self.logger.info("post import data:%s" % url)
        
class GetTaokCate(object):
    def __init__(self, ):
        self.logger = logging.getLogger("taoke")
        
    def __call__(self, site, http, next_task, url, local_url, *args):
        local_abs_path = site.real_path(local_url)
        if os.path.isfile(local_abs_path):
            self.logger.info("the topic is exist in local:%s, local:%s" % (url, local_abs_path))
            return
        
        try:
            self.logger.info("open url:%s" % url)
            output_text = http.get(url)
        except:
            output_text = 'error to get url.'		
            pass
        self.logger.info("-----------%s   --------------" % url);
        self.logger.info(output_text)
        sleep(1)

class GetTaokDetailOld(object):
    def __init__(self, ):
        self.logger = logging.getLogger("taoke")
        self.taobao = Taobao('12570801', 'fbab4f2ded890ae889e876ae0eee90b9')
        self.oss = OssAPI("storage.aliyun.com", "dcixul0kll5ubeisualf3q1d", "1fMUf01mRTfjXe/Ub4qEmLiu7tU=")
        
    def __call__(self, site, http, next_task, url, local_url, *args):
        local_abs_path = site.real_path(local_url)
        if os.path.isfile(local_abs_path):
            self.logger.info("the topic is exist in local:%s, local:%s" % (url, local_abs_path))
            return
        
        #self.logger.info("start fetch topic, url:%s" % url)
        #data = http.get(url)
        self.taobao.http = http
        num_iid = re.search(r"/(\d{7,})/", url).group(1)
        self.logger.info("start fetch taoke details id:%s" % num_iid)
        
        try:
            data = self.taobao.taobao_item_get(fields='detail_url,num_iid,title,nick,type,cid,seller_cids,props,input_pids,input_str,desc,pic_url,num,valid_thru,list_time,delist_time,stuff_status,location,price,post_fee,express_fee,ems_fee,has_discount,freight_payer,has_invoice,has_warranty,has_showcase,modified,increment,approve_status,postage_id,product_id,auction_point,property_alias,item_img,prop_img,sku,video,outer_id,is_virtual', 
                num_iid=num_iid)
            data = data.get('item_get_response')
        except Exception, e:
            if e.__class__.__name__ == 'TaobaoException' and 'isv.' in e.sub_code: # == 'isv.item-is-delete:invalid-numIid-or-iid':
                self.logger.info("expired taoke id:%s" % num_iid)
                remove_url = "http://%s/queue/expired_taoke/" % site.hostname
                http.post_data(remove_url, {'num_iid': num_iid})
                return
            else:
                raise

        #self.logger.info("data:%s" % data)
        
        data['item']['traderates'] = self.get_comments(num_iid, data['item']['nick'])
        self.logger.info("start fetch main images...")
        index = 0
        main_image = [e['url'] for e in data['item']['item_imgs']['item_img'] ]
        (main_image, index) = self.save_image_to_oss(main_image, index, http, site, num_iid)
        
        self.logger.info("start fetch desc images...")
        desc_images = self._parse_image_from_desc(data['item']['desc'])        
        (desc_images, index) = self.save_image_to_oss(desc_images, index, http, site, num_iid)
        
        data['item']['main_images'] = main_image
        data['item']['desc_images'] = desc_images
        #print data
        if os.environ.get('HUDSON_URL'):
            http.post_data("http://127.0.0.1:8924/queue/q/imported_taoke?format=json", {'details': json.dumps(data['item']), 'num_iid': num_iid}, {})
        else:
            http.post_data("http://data.deonwu84.com/queue/q/imported_taoke?format=json", {'details': json.dumps(data['item']), 'num_iid': num_iid}, {})
        http.post(url, site.real_path("log/%s/%s.txt" % (num_iid[-1:], num_iid)), {'data': json.dumps(data['item'])})
        self.save_topic_data(data, local_abs_path)
        self.logger.info("done process taoke, id:%s" % num_iid)
        
    def get_comments(self, num_iid, nick):
        data = self.taobao.taobao_traderates_search(num_iid=num_iid, seller_nick=nick, )
        return data.get("traderates_search_response", {}).get("trade_rates", {}).get('trade_rate', [])
        
    def save_topic_data(self, topic, local_path):
        if not exists_path(dir_name(local_path)): make_path(dir_name(local_path))
        
        fd = open(local_path, 'w')
        fd.write(json.dumps(topic))
        fd.close()
        
    def save_image_to_oss(self, images, index, http, site, num_iid):
        data = {}
        path = strftime("%m%d", localtime())
        
        local_thumb = ''
        for url in images:
            index += 1
            local = site.real_path("taoke/%s/%s/%s_%s.jpg" % (path, num_iid, num_iid, index))
            
            thumb_url = "taoke/%s/%s/%s_%s_thumb.jpg" % (path, num_iid, num_iid, index)
            local_thumb = os.path.join('/opt/data', thumb_url) #site.real_path(thumb_url)
            try:
                http.download(url, local)
                import Image
                im = Image.open(local)
                (w, h) = im.size
                if w < 200 or h < 200: continue
                im.thumbnail((128, 128), Image.ANTIALIAS)
                if not exists_path(dir_name(local_thumb)): make_path(dir_name(local_thumb))
                im.save(local_thumb)
                #if self._save_to_oss(thumb_url, local_thumb, num_iid):
                data[url] = 'http://data.deonwu84.com/%s' % thumb_url
                self.logger.info("thumbnail %s -> %s " % (url, data[url]))
            except Exception, e:
                logging.info("error:%s" % e)
                data[url] = url
                
        return (data, index)

    def _save_to_oss(self, path, local_path, num_iid):
        content_type = "image/jpeg"
        res = self.oss.put_object_from_file("fmei_st", path, local_path, content_type, {'num_iid': num_iid})
        if (res.status / 100) == 2:
            return True
        else:                    
            logging.info("put_object_from_file ERROR")                
        return False
    
    def _parse_image_from_desc(self, text):
        #img src="http://img02.taobaocdn.com/imgextra/i2/228784630/T2emyBXolXXXXXXXXX_!!228784630.jpg"
        links = re.compile(r'((src|background)=(\'[^\']*\'|"[^"]*"|[^\s>]*))', re.I)
        
        images = []
        for i in links.finditer(text):
            url = i.group(3).strip("'").strip('"')
            images.append(url)
                     
        return images        
        