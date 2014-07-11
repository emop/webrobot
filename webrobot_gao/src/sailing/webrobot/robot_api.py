'''
Created on 2013-7-10

@author: deonwu
'''

from time import localtime, strftime
import os
import json
import urllib
import logging
import hashlib


class Robot(object):
    def __init__(self, app_id = None, app_secret = None, host='http://emopad.sinaapp.com/robot/api/proxy'):
        #http://gw.api.taobao.com/router/rest
        #'http://gw.api.tbsandbox.com/router/rest?'
        self.app_id = app_id
        self.app_secret = app_secret or '995a5637240add612dfd30945adf1c99'
        self.host = host
        self.http = self._default_http()

    def __getattr__(self, name):
        if not name.startswith("__"):
            return CallProxy(name, self.http, self.app_secret, self.host)
        else:
            raise AttributeError("Not found attr '%s'" % name)


    def _default_http(self, ):
        from captcha.http_client import HTTPClient
        
        return HTTPClient()
            
class CallProxy(object):

    def __init__(self, name, http, secret, end_point_url):
        self.name = name
        self.http = http
        self.secret = secret
        self.host = end_point_url

    def __call__(self, **kw):
        param = {'name': self.name, 'param': json.dumps(kw)}
        
        key = "%s%s%s" % (self.name, json.dumps(kw), self.secret)
        
        sign = hashlib.md5(key).hexdigest().lower()
        
        param['sign'] = sign
        
        resp = self.http.post_data(self.host, param, {}) 

        data = json.loads(resp, 'utf-8')
        return data

            
