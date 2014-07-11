from sailing.common.utils import import_class
from sailing.common.common import *
import sys, os, time
class Management():
    
    def __init__(self, argv=None):
        self.argv = argv or sys.argv
                
    def execute(self):
        if len(self.argv) != 3:
            print 'python -m sailing start|stop <application>'
            sys.exit()
        
        if hasattr(time, 'tzset'):
            os.environ['TZ'] = 'Asia/Shanghai'
            time.tzset()
    
        self.command = self.argv[1]
        if os.path.isdir('libs'):
            sys.path.insert(0, 'libs')
            
        command = "sailing.core.commands.%s.Command" % self.command
        cmd_cls = import_class(command)
        
        if cmd_cls is None: raise Exception("Not found command '%s'" % self.command)
                
        cmd = cmd_cls()
        cmd.execute(*self.argv[2:])
            
    def load_command(self, name):
        pass

    def _setting_logging(self):
        import logging.config
        from common.common import join_path
        
        logging.config.fileConfig(join_path(dir_name(__file__), "logging.ini"))
    
