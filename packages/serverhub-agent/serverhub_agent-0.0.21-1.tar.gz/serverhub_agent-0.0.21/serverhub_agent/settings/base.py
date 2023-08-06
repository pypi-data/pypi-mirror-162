from serverhub_agent.settings import _env_variables
from serverhub_agent.ws.output_processor import BaseOutputProcessor


def init_settings_from_env(app):
    app['FS_EXPOSED_DIR'] = _env_variables.FS_EXPOSED_DIR
    app['ENTRYPOINT_DIR'] = _env_variables.ENTRYPOINT_DIR
    app['REQUEST_MAX_BODY_SIZE_MB'] = _env_variables.REQUEST_MAX_BODY_SIZE_MB
    app['STARTUP_TIMEOUT'] = _env_variables.STARTUP_TIMEOUT
    app['PORTS_TO_WAIT'] = _env_variables.PORTS_TO_WAIT
    app['PORTS_TO_WAIT_RESPONDING'] = _env_variables.PORTS_TO_WAIT_RESPONDING
    app['PROC_MEM_LIMIT_MB'] = _env_variables.PROC_MEM_LIMIT_MB
    app['WAIT_ON_PUT'] = _env_variables.WAIT_ON_PUT
    app['INTERPRETER_NAME'] = _env_variables.INTERPRETER_NAME
    app['SCRIPT_NAME'] = _env_variables.SCRIPT_NAME
    app['ENTRYPOINT_PATH'] = _env_variables.ENTRYPOINT_PATH
    app['ENTRYPOINT_LOGS_PATH'] = _env_variables.ENTRYPOINT_LOGS_PATH
    app['PROC_OUTPUT_LIMIT'] = 2 ** 20
    app['PROC_OUTPUT_BUFFER_SIZE'] = 2 ** 16
    app['OUTPUT_PROCESSOR_CLS'] = BaseOutputProcessor
