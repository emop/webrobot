
class BaiduSearch(object):
    def __init__(self):
        pass
    
    def __call__(self, client, api, **kw):
        """
        client -- 
        client
        api --
        
        """
        
        client.driver.get("http://www.baidu.com")
                
        input = client.e("#kw")
        input.clear()
        input.send_keys(kw['keyword'])
        
        submit = client.e("#su")
        submit.click()
        
        #path = client.real_path("screen.png")
        client.screenshot_as_file("screen.png")
        
        result_list = client.es(".result tr div.f13")
        for item in result_list:
            print item.text
        
        
        
        
        print "kw:%s" % str(kw)
