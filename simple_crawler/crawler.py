# -*- coding: gbk -*-
"""
HTTP Client
http://www.hzfc365.com/house_search/search_prj.jsp?lpid=1374
"""

import sys, os, logging, re

from http_client import HTTPClient
class SimpleCrawler(object):
    def __init__(self):
        self.http = HTTPClient()
        self.debug = True
        
    def start(self, lpid):
        url = "http://www.hzfc365.com/house_search/search_prj.jsp?lpid=%s" % lpid
        reps_text = self.http.download(url)
        if self.debug:
            self._save_temp(reps_text, lpid)
        build_list = self.parse_build_info(reps_text)
        for build in build_list:
            logging.info("start fetch:%s, Kai Pan Shi jian:%s" % (1, 2))
            build.lpid = lpid
            for zh_nm in build.zh_nm_list:
                self.fetch_zh_nm_pid_data(build, *zh_nm)
    
    def fetch_zh_nm_pid_data(self, build, zh_nm, pid, name):
        url = "http://www.hzfc365.com/house_view/lpxx-xs-2.jsp"\
              "?zh_nm=%s&pid=%s" % (zh_nm, pid)
        referer_url = "http://www.hzfc365.com/house_search/search_prj.jsp?lpid=%s" % build.lpid
        reps_text = self.http.download(url, {"Referer": referer_url})
        if self.debug:
            self._save_temp(reps_text, zh_nm)
        self._parse_room_info(reps_text, referer_url=url)
        
    def _parse_room_info(self, reps_text=None, cache_name = None, referer_url=None):
        if cache_name: reps_text = self._read_temp(cache_name)
        #http://www.hzfc365.com/house_view/lpxx-xs-2.jsp?zh_nm=120620&pid=87401
        """http://www.hzfc365.com/house_view/lpxx-xs-2-yt.jsp?zh_nm=120618&q_area=&keytime=1288790113772&sessionid=2ECA879E33D7BECC3941443553DAD4FC"""
        """http://www.hzfc365.com/house_view/lpxx-xs-2-yt.jsp?
        zh_nm=120618&
        q_area=&
        keytime=1288790113772& 
                //12887910169
        sessionid=2ECA879E33D7BECC3941443553DAD4FC"""
        r_zh_nm = re.search('<input id="info_zh_nm" type="hidden" value="(\d+)">', reps_text).group(1)
        sessionid = re.search('<input id="sessionid" type="hidden" value="(\w+)">', reps_text).group(1)
        import time
        cur_time = time.time()
        
        logging.info("r_zh_nm=%s, sessionid=%s, time=%s" % (r_zh_nm, sessionid, cur_time))
        url = "http://www.hzfc365.com/house_view/lpxx-xs-2-yt.jsp?zh_nm=%s&q_area=&keytime=%s&sessionid=%s" % (r_zh_nm, cur_time * 100, sessionid)
        
        reps_text = self.http.download(url, {"Referer": referer_url})
        if self.debug:
            self._save_temp(reps_text, "d%s" % r_zh_nm)
        return self._parse_room_detail_info(reps_text)     
                    
    def _parse_room_detail_info(self, reps_text=None, cache_name=None):
        if cache_name: reps_text = self._read_temp(cache_name)
        regex = "title='([^']+)'"
        factor = re.compile(regex, re.I)
        data = []
        for item in factor.finditer(reps_text):
            logging.info("details:%s" % str(item.groups()))
            data.append(RoomInfo(*item.groups()))
        return data
        #<input id="info_zh_nm" type="hidden" value="120620">
        #<input id="sessionid" type="hidden" value="27D3C558B4A632ABFE27FC1B48ADAB44">

                
        
    
    def parse_build_info(self, reps_text=None, cache_name = None):
        if cache_name: reps_text = self._read_temp(cache_name)
        td = r"\s+<td[^>]+>(.*?)</td>" 
        regex = r"<TR onmouseover=[^>]+><A [^>]+>%s</A>" % (td * 7)
        regex += "\s+<td[^>]+>(.*?)</td>"
        regex += "\s+</tr>"
        factor = re.compile(regex, re.I)
        #items = ( e.group(1) for e in factor.finditer(expr) )
        data = []
        for item in factor.finditer(reps_text):
            logging.info("data:%s" % str(item.groups()))
            data.append(BuidingInfo(*item.groups()))
        return data
            
    
    def _save_temp(self, data, name):
        fd = open("temp_cache_%s.txt" % name, "w")
        fd.write(data)
        fd.close()
        
    def _read_temp(self, name):
        data = ""
        fd = open("temp_cache_%s.txt" % name, "r")
        data = fd.read()
        fd.close()
        return data

class BuidingInfo(object):
    def __init__(self, yszh, kpsj, ksts, ksmj, ysts, ysjj, yydts, ysds):
        self.id = None
        self.yszh = yszh
        self.kpsj = kpsj
        self.ksts = ksts
        self.ksmj = ksmj
        self.ysts = ysts
        self.ysjj = ysjj
        self.yydts = yydts
        self.ysds = ysds
        #yszh, kpsj, ksts, ksmj, ysts, ysjj, yydts, ysds
        #self.rooms = {}
        self.zh_nm_list = self._parse_zh_nm_list(ysds)
        
    def _parse_zh_nm_list(self, ysds):
        regex = r'<a href=".*?zh_nm=(\d+)&pid=(\d+)".*?>(.*?)</a>'
        factor = re.compile(regex, re.I)
        data = []
        for item in factor.finditer(ysds):
            logging.info("data:%s" % str(item.groups()))
            data.append(item.groups())
        return data
        
        #<a href="/house_view/lpxx-xs-2.jsp?zh_nm=119218&pid=86101" target="_blank" class="main">2\xb4\xb1</a>&nbsp;

class RoomInfo(object):
    def __init__(self, data):
        self.id = None
    
def main(lpid):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.info("starting process lpid:%s" % lpid)
    
    crawler = SimpleCrawler()
    crawler.debug = True
    
    lpid = "1374"
    crawler.start(lpid)
    #xxx = crawler.parse_build_info(None, "1374")
    #build = lambda:1
    #build.lpid = "1374"
    #crawler.fetch_zh_nm_pid_data(build, "120620", "87401", "4")
    #crawler._parse_room_detail_info(None, "d120620")
    
    logging.info("end process lpid %s." % lpid)    

if "__main__" == __name__:
    main("")
    if len(sys.argv) != 2:
        print "python crawler.py <lpid>"
    else:
        main(sys.argv[1])
        
        