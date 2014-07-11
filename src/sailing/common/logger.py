from common import *

class Logger(object):

    TRACE = 'TRACE'
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    
    LOG_LEVELS = [TRACE, DEBUG, INFO, WARN, ERROR]
    
    def __init__(self, 
                 name='log', path=None, 
                 level=DEBUG, size=2000000, rotation=5, 
                 notifier=Notifier(), notification_level=ERROR, print_message=True):
        self.name = name
        self.path = path and path or current_path()
        self.level = level
        self.size = size
        self.rotation = rotation
        self.notifier = notifier
        self.notification_level = notification_level
        self.print_message = print_message
        
        self.file = join_path(self.path, self.name)
        self.fd = None
    
        make_path(self.path)
    
    def __del__(self):
        self.close_fd()
                
    def log(self, msg, level=DEBUG, notify=True):
        msg = '%s - %s - %s' % (time_to_str(), level, type(msg) == type('') and msg or str(msg))
        if self.LOG_LEVELS.index(level) >= self.LOG_LEVELS.index(self.level):
            self.get_fd()
            self.fd.write(msg)
            self.fd.write('\n')
            self.fd.flush()
            if self.print_message:
                print msg
        if notify \
           and self.notifier \
           and self.LOG_LEVELS.index(level) >= self.LOG_LEVELS.index(self.notification_level):
            try:
                self.notifier.notify('Logger', msg)
            except:
                self.log(trackable('Failed to call notifier'), self.ERROR, False)
        return msg
    
    def trace(self, msg):
        return self.log(msg, self.TRACE)
        
    def debug(self, msg):
        return self.log(msg, self.DEBUG)
    
    def info(self, msg):
        return self.log(msg, self.INFO)
    
    def warn(self, msg):
        return self.log(msg, self.WARN)
    
    def error(self, msg):
        return self.log(msg, self.ERROR)
        
    def get_fd(self):
        if exists_path(self.file) and file_size(self.file) > self.size:
            self.close_fd()
            for ix in range(self.rotation, 0, -1):
                if ix == self.rotation and exists_path('%s%d' % (self.file, ix)):
                    remove_path('%s%d' % (self.file, ix))
                elif exists_path('%s%d' % (self.file, ix)):
                    move_to('%s%d' % (self.file, ix), '%s%d' % (self.file, ix+1))
            move_to(self.file, '%s%d' % (self.file, 1))
#            copy_to(self.file, '%s%d' % (self.file, 1))
#            try:
#                self.fd = open(self.file, 'a')
#                self.fd.truncate()
#            except:
#                remove_path(self.file)
        if not self.fd:
            try:
                self.fd = open(self.file, 'a')
            except:
                raise Exception,  trackable('Could not open log file %s' % self.file)

    def close_fd(self):
        if self.fd:
            try:
                self.fd.close()
                self.fd = None
            except:
                raise Exception,  trackable('Could not close log file %s' % self.file)
            
if __name__ == '__main__':
    logger = Logger(size=1)
    for ix in range(logger.rotation+2):
        logger.debug(ix)
    
    logger = Logger(name='positive', level=Logger.INFO)
    logger.debug('debug')
    logger.info('info')
    logger.error('error')
    
    class MyNotifier(object):
        def notify(self, source, msg):
            raise Exception, 'Notification: source = %s; message = %s' % (source, msg)
    logger = Logger(name='negative', level=Logger.INFO, notifier=MyNotifier())
    logger.debug('debug')
    logger.info('info')
    logger.error('error')