from sailing.common.common import *
from sailing.common.notifier import NOTIFIER
import os
from sailing.conf import ENVIRONMENT_VARIABLE
APP_NAME = os.environ[ENVIRONMENT_VARIABLE]

DATA_ROOT = os.getcwd()

ABNORMAL_NOTIFIER = NOTIFIER 

LOG_NAME = '%s.log' % APP_NAME
LOG_PATH = join_path(DATA_ROOT, 'logs')
LOG_LEVEL = 'TRACE'
LOG_SIZE = 2000000
LOG_ROTATION = 20 
LOG_NOTIFIER = ABNORMAL_NOTIFIER 
LOG_NOTIFICATION_LEVEL = 'ERROR'

MINIMAL_FILE_AGE = 1
POLLING_INTERVAL = 2

IDLE_INTERVAL = 1 * 60

RUNNING_FLAG = join_path(DATA_ROOT, '.%s_running' % APP_NAME)
CLOSING_FLAG = join_path(DATA_ROOT, '.%s_closing' % APP_NAME)

TIME_ZONE = 'RPC'

