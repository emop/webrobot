# -*- coding: utf-8 -*-
import hashlib
from time import localtime, strftime
import os
import json
import urllib
#os.environ['TZ'] = 'Asia/Shanghai'
#tzset()
#'2012-04-14 10:03:00'


class Taobao(object):
    def __init__(self, app_id, app_secret, http=None, host='http://gw.api.taobao.com/router/rest?'):
        #http://gw.api.taobao.com/router/rest
        #'http://gw.api.tbsandbox.com/router/rest?'
        self.app_id = app_id
        self.app_secret = app_secret
        self.http = http or self._default_http()
        self.param = {'app_key': app_id,  
                      'app_secret': app_secret,
                      }
        self.host = host
    
    def __getattr__(self, name):
        if not name.startswith("__"):
            name = name.replace("_", ".")
            return CallProxy(name, self._api_param_order(name), self.param, self.http, self.host)
        else:
            raise AttributeError("Not found attr '%s'" % name)
        
    def _api_param_order(self, name):
        return {
            'taobao.itemcats.get': ['fields', 'parent_cid', 'cids'],
            'taobao.item.get': ['fields', 'num_iid'],
            'taobao.traderates.search': ['num_iid', 'seller_nick', 'page_no', 'page_size'],
        }.get(name, [])
        
    def _default_http(self, ):
        class httpClient(object):
            def get(self, url):
                data = None
                req = urllib.urlopen(url)
                data = req.read()
                return data
        return httpClient()

class TaobaoException(Exception):
    def __init__(self, data):
        super(TaobaoException, self).__init__(data.get('msg'))
        self.sub_code = data.get("sub_code")
        self.code = data.get("code")
        self.sub_msg = data.get("sub_msg")
        
class CallProxy(object):
    
    def __init__(self, name, app_order, sys_param, http, host):
        self.sys_order = ['method', 'session', 'timestamp', 'format', 'app_key', 'v', 'sign', 'sign_method']
        self.app_order = app_order
        self.sys_param = sys_param
        self.http = http
        self.host = host
        self.sys_param['method'] = name
        
    def __call__(self, **kw):
        self.sys_param['timestamp'] = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.sys_param['v'] = '2.0'
        self.sys_param['sign_method'] = 'md5'
        self.sys_param['format'] = 'json'
        
        sign = self._get_sign(self.sys_param, kw)        
        str_param = self._create_str_param(self.sys_param, kw)
        str_param = '%s&sign=%s' % (str_param, sign)     
        api_url = '%s%s' % (self.host, str_param)
                
        resp = self.http.get(api_url)        
        resp = resp.replace("\r", "\\r").replace("\n", "\\n")
        
        data = json.loads(resp, 'utf-8')
        if data.get('error_response'):
            raise TaobaoException(data.get('error_response'))
        return data
        
    def _get_sign(self, sys_param, app_param):
        b = dict(sys_param)
        b.update(app_param)
        
        param_order = self.sys_order + self.app_order
        param_order.sort()
        params = [ u"%s%s" % (e, b.get(e)) for e in param_order if unicode(b.get(e, '')).strip() ]
        
        secret = sys_param['app_secret']
        str_param = u"".join(params)
        str_param = u"%s%s%s" % (secret, str_param, secret,)
        #print "xx:%s" % str_param
        
        return hashlib.md5(str_param.encode("utf-8")).hexdigest().upper()
        
        
    def _create_str_param(self, sys_param, app_param):
        b = dict(sys_param)
        b.update(app_param)
        
        param_order = self.sys_order + self.app_order
        
        
        params = [ u"%s=%s" % (e, urllib.quote(b.get(e).encode("utf-8"))) for e in param_order if unicode(b.get(e, '')).strip() ]
        
        str_param = u"&".join(params)
        return str_param
        
        
        
        