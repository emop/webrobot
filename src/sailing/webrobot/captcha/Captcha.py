'''
Created on 2013-7-5

@author: deonwu
'''
import base64
from http_client import HTTPClient
import json

def get_captcha(path, group='emop'):
    fd = open(path, 'rb')
    
    data = base64.b64encode(fd.read())
    fd.close()
    
    client = HTTPClient()
    
    param = {'g': group, 'content': data}
    
    response = client.post_data("http://192.168.3.220:8000/route", param, {})
    #response = client.post_data("http://127.0.0.1:8925/route", param, {})
    print("the response : %s" % response)
    if response:    
        ret = json.loads(response)    
    else:
        ret = {}
        
    return ret