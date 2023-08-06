from ._tools import get_setting

FS_EXPOSED_DIR = get_setting('FS_EXPOSED_DIR', default='/app/')
ENTRYPOINT_DIR = get_setting('ENTRYPOINT_DIR', default='/.utils/')
REQUEST_MAX_BODY_SIZE_MB = get_setting('REQUEST_MAX_BODY_SIZE_MB', default=30)
STARTUP_TIMEOUT = get_setting('STARTUP_TIMEOUT', default=50)
PORTS_TO_WAIT = get_setting('PORTS_TO_WAIT', default='3000').split(',')
PORTS_TO_WAIT_RESPONDING = get_setting('PORTS_TO_WAIT_RESPONDING', default='').split(',')
PROC_MEM_LIMIT_MB = get_setting('PROC_MEM_LIMIT_MB', default=512)
WAIT_ON_PUT = get_setting('WAIT_ON_PUT', default=True)
INTERPRETER_NAME = get_setting('INTERPRETER_NAME', default='python')
SCRIPT_NAME = get_setting('SCRIPT_NAME', default='__test.py')
ENTRYPOINT_PATH = get_setting('ENTRYPOINT_PATH', default='/.utils/entrypoint.sh')
ENTRYPOINT_LOGS_PATH = get_setting('ENTRYPOINT_LOGS_PATH', default='/.utils/logs')
