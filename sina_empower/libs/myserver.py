#-*- coding: utf8 -*-
import TaodianApi
import json
import time
import os
import string

print "start"
def file_exist():
	filelist = os.listdir("../webrobot/")
	exist = False
	mx = "0001"
	for f in filelist:
		temp = f.split(".", 1)
		if mx < temp[0]:
			mx = temp[0]
		#if temp[1] == "running" or temp[1] == "waiting" :
		#	exist = True
	return {"status":exist, "filename":mx}
	
def write_plan(filename, tasklist):
	filename = string.atoi(filename)+ 2
	filename = "../webrobot/%04d.waiting" % filename
	print filename
	fl = open(filename,"w")
	for ts in tasklist:
		fl.write(ts+"\r\n")
	fl.close()
	print "waiting"
		
try:
	api = TaodianApi.TaodianApi()
	while True:
		fe = file_exist()
		if fe["status"] :
			print "has waiting"
		else:
			param = {"time":"111111"}
			plan = api.call("fans_scan_plan_list", param)
			print plan
			data = plan["data"]["data"]
			#weibo_list = api.call("timing_weibo_account_list",{})
			#weibo_list = weibo_list["data"]["data"]
			weibo_data = "login_user=%s,login_passwd=%s" % ("helloaction@126.com","xingkong")
			tasklist = []
			t = time.localtime(time.time())
			ref_time = time.localtime(time.time() - 60*60*24*2)
			task_plan = time.strftime("%m%d", t)
			task_id = string.atoi(time.strftime("%H%M%S", t))
			for d in data:
				#weibo_data = "login_user=%s,login_passwd=%s" % (weibo_list[i]["login_user"],  weibo_list[i]["login_password"])
				#task_id = task_id + 1
				db_time =time.strptime(d["last_update_time"], "%Y-%m-%d %H:%M:%S")
				if d["last_update_time"] == d["create_time"] or ref_time > db_time:
					nick = "%s:%d-->%s@wb_account=%s,%s" % (task_plan, task_id, "send",d["nick"].encode("utf8"),weibo_data.encode("utf8"))
					tasklist.append(nick)
				
			write_plan(fe["filename"], tasklist)

		time.sleep(60*60*5)
except:
	pass



