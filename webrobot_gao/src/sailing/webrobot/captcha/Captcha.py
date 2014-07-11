'''
Created on 2013-7-5

@author: deonwu
'''
import base64
from http_client import HTTPClient
import json

def get_captcha(path, group='emop'):
    fd = open(path, 'r')
    
    data = base64.b64encode(fd.read())
    fd.close()
    
    client = HTTPClient()
    
    param = {'g': group, 'content': data}
    
    response = client.post_data("http://42.120.43.111:8925/route", param, {})
    #response = client.post_data("http://127.0.0.1:8925/route", param, {})
    
    if response:    
        ret = json.loads(response)    
    else:
        ret = {}
        
    return ret