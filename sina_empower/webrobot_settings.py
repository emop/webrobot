

#PROXY = {'http': 'http://10.144.1.10:8080'}
#

ACTIONS = {'sina_empower': ('actions.SinaBatchEmpower', {}),
           'user_login': ('actions.SinaBatchEmpower', {}),
           'no_user': ('actions2.SinaSmsActivate',{}),
           'send': ('actions3.SendConpon', {}),
           }

WORK_THREAD_COUNT = 1
#BROWSER_NAME = "firefox"  #phantomjs
BROWSER_NAME = "phantomjs"  #phantomjs
