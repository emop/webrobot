from sailing.core.application import Application
from sailing.conf import settings

class Command(object):
    
    def execute(self, name, level='DEBUG',**para):
        settings.configure(name)
        
        app = Application()
        app.daemon = False
        #app.logger.info("start application %s" % name)
        app.prepare(level)
        app.run()
        app.logger.info("done")
