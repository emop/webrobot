
from sailing.core.application import Application
from sailing.conf import settings

class Command(object):
    
    def execute(self, name, **para):
        settings.configure(name)
        Application().stop()