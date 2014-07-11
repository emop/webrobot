# -*- coding: utf8 -*-

import os
import re
import sys
import locale
import SimpleHTTPServer
import SocketServer
import subprocess
import StringIO

"""
如果要在网关上切换IP。就不要服务的Listen 地址设置为0.0.0.0. 如果外网地址发生变化，容易出现
接口连接错误。重启服务的时候，要出现地址已经绑定。无法释放。只监听内网的端口，可以避免IP变化
导致错误。
"""
addr = len(sys.argv) < 2 and "192.168.3.200" or sys.argv[1]
port = len(sys.argv) < 3 and 8090 or locale.atoi(sys.argv[2])

class MyHander(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._switch_ip()
    
    def do_POST(self):
        self._switch_ip()
        
    def _switch_ip(self):
        self.send_response(200)
        self.end_headers()
        
        if "switch_ip" in self.path:
            subprocess.call("pppoe-stop && pppoe-start && ifconfig ppp0 |grep 'inet addr'", shell=True, stderr=self.wfile, stdout=self.wfile)
            print "---\n" 
            subprocess.call("ifconfig ppp0 |grep 'inet addr'", shell=True)
    
            self.wfile.write("\n\ndone") 
        else:
            self.wfile.write("/switch_ip -- switch new ip") 

#handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer((addr, port), MyHander)
print ("HTTP server is at: http://%s:%d/" % (addr, port))
httpd.serve_forever()