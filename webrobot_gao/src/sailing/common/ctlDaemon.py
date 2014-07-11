from common import *
from logger import Logger
from pyDaemon import createDaemon

class StatusException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        
class ControllableDaemon(object):
    ERROR_ALREADY_STARTED = 1
    ERROR_CLOSING_IN_PROGRESS = 2
    ERROR_EMPTY_BUSINESS_FUNC = 3

    MSG_ERROR_ALREADY_STARTED = 'Already started'
    MSG_ERROR_CLOSING_IN_PROGRESS = 'Closing in progress'
    MSG_ERROR_EMPTY_BUSINESS_FUNC = 'Empty business functions -'\
                                    ' run is mandatory to be implemented by user'\
                                    ' while prepare and finish are optional'
    
    def __init__(self, name='controllable daemon', running_flag='.running', closing_flag='.closing', daemon=True):
        self.name = name
        self.running_flag = running_flag
        self.closing_flag = closing_flag
        self.daemon = daemon
        self.force_flag = False
        self.logger = None
        
    def is_running(self):
        return exists_path(self.running_flag)
    
    def is_closing(self):
        return exists_path(self.closing_flag)
    
    def is_forced(self):
        return self.force_flag
    
    def set_running_flag(self):
        make_path_as_lock(self.running_flag, True)
    
    def set_closing_flag(self):
        make_path_as_lock(self.closing_flag, True)

    def set_force_flag(self):
        self.force_flag = True
        
    def unset_running_flag(self):
        remove_path(self.running_flag)
        
    def unset_closing_flag(self):
        remove_path(self.closing_flag)
    
    def unset_force_flag(self):
        self.force_flag = False
        
    def start(self):
        if self.is_running():
            raise StatusException, (self.ERROR_ALREADY_STARTED, self.MSG_ERROR_ALREADY_STARTED)
        self.set_running_flag()
        import platform
        if os.sep == ('/') and platform.system() == 'Linux':
            if self.daemon:
                print '%s started as daemon' % self.name
                createDaemon()
            else:
                print '%s suspended to start as daemon' % self.name
        else:
            print '%s started' % self.name
        self.prepare()
        interrupted = False
        while not interrupted and not self.is_closing():
            try:
                self.run()
            except KeyboardInterrupt:
                print 'Interrupted by user'
                interrupted = True
            except:
                print self.logger.error(trackable('Interrupted by exception'))
                interrupted = True
        self.finish()
        self.logger.info('%s stopped' % self.name)
        print '%s stopped' % self.name
        self.unset_running_flag()

    def forcestart(self):
        if self.is_running() and user_input('CAUTIOIN: running flag is set, are you sure? (y|n) ') != 'y':
            return
        self.unset_running_flag()
        if self.is_closing() and user_input('CAUTIOIN: closing flag is set, are you sure? (y|n) ') != 'y':
            return
        self.unset_closing_flag()
        self.set_force_flag()
        self.start()
        
    def stop(self):
        if self.is_closing():
            raise StatusException, (self.ERROR_CLOSING_IN_PROGRESS, self.MSG_ERROR_CLOSING_IN_PROGRESS)
        self.set_closing_flag()
        try:
            while self.is_running():
                sys.__stdout__.write('-')    
                for iy in '\\|/-' * 30:
                    sys.__stdout__.write(chr(8) + iy)
                    sys.__stdout__.flush()
                    sleep(0.25)
                    if not self.is_running():
                        sys.__stdout__.write(chr(8))
                        sys.__stdout__.flush()
                        break
            print '%s stopped' % self.name
        except KeyboardInterrupt:
            print 'Operation canceled by user'
        self.unset_closing_flag()
    
    def prepare(self):
        self.logger = Logger()
        
    def run(self):
        raise StatusException, (self.ERROR_EMPTY_BUSINESS_FUNC, self.MSG_ERROR_EMPTY_BUSINESS_FUNC)
    
    def finish(self):
        pass
