from common import *

class Notifier(object):
    def __init__(self):
        pass
    
    def notify(self, source, *args):
        if source == 'Logger':
            print 'Logger: error log message caught - %s' % args[0]
        elif source == 'Dispatching':
            reason, path = args
            print 'Dispatching: invalid file caught - %s - %s' % (reason, path)
        elif source == 'Validation':
            reason, path = args
            print 'Validation: invalid file caught - %s - %s' % (reason, path)
        else:
            print 'Notification: source = %s; message = %s' % (source, str(args))
            
NOTIFIER = Notifier()