
"""
Settings and configuration for Sailing.

Values will be read from the module specified by the SAILING_SETTINGS_MODULE environment
variable; see the global settings file for
a list of all possible variables.
"""

import os
import time     # Needed for Windows

ENVIRONMENT_VARIABLE = "APP_NAME"

class LazySettings(object):
    
    def __init__(self):
        # _target must be either None or something that supports attribute
        # access (getattr, hasattr, etc).
        self._target = None
        self._app_settings = None

    def __getattr__(self, name):
        if self._target is None:
            self._import_settings()
        if name == '__members__':
            # Used to implement dir(obj), for example.
            return self._target.get_all_members()
        return getattr(self._target, name)

    def __setattr__(self, name, value):
        if name in ['_target', '_app_settings']:
            # Assign directly to self.__dict__, because otherwise we'd call
            # __setattr__(), which would be an infinite loop.
            self.__dict__[name] = value
        else:
            if self._target is None:
                self._import_settings()
            setattr(self._target, name, value)

    def _import_settings(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        try:
            app_name = os.environ[ENVIRONMENT_VARIABLE]
            if not app_name: # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            # NOTE: This is arguably an EnvironmentError, but that causes
            # problems with Python's interactive help.
            raise ImportError("Settings cannot be imported, because environment variable %s is undefined." % ENVIRONMENT_VARIABLE)
        
        if self._app_settings is None:
            self._app_settings = "%s_settings" % app_name 
            
        global_settings = "sailing.conf.global_%s_settings" % app_name 
        
        self._target = Settings(['sailing.conf.global_settings', global_settings, self._app_settings])
    
    def configure(self, app_name='', app_settings=None, **options):
        
        if self._target != None:
            raise RuntimeError, 'Settings already configured.'
        if not app_name: raise RuntimeError, 'Application name is required.'
        
        os.environ[ENVIRONMENT_VARIABLE] = app_name
        self._app_settings = app_settings

    def configured(self):
        """
        Returns True if the settings have already been configured.
        """
        return bool(self._target)
    configured = property(configured)

class Settings(object):
    def __init__(self, settings):
                
        for mod in settings:
            try:
                mod = __import__(mod, {}, {}, [''])
            except ImportError, e:
                print "Could not import settings '%s'" % mod
                
            for setting in dir(mod):
                if setting.isupper():
                    setting_value = getattr(mod, setting)
                    setattr(self, setting, setting_value)
            

    def get_all_members(self):
        return dir(self)
    

settings = LazySettings()

