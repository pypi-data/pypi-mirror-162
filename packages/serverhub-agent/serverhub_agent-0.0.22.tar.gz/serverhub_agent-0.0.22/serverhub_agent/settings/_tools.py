import os
from typing import TypeVar


class EnvType:
    """
    Available env types.
    """
    local = 'local'


class CodeRunnerType:
    """
    Available code runners.
    """
    subprocess = 'subprocess'
    swarm = 'swarm'


V = TypeVar('V')


def get_setting(name: str, default: V = None, cast: type = None, required: bool = False):
    """
    Get settings from env vars.
    """
    value: V = os.getenv(name)

    if value is None:
        if required:
            raise EnvironmentError(f'Required setting "{name}" not found in environment')
        return default

    if default is not None and cast is None:
        cast = type(default)
    elif cast is None:
        cast = str

    if cast is bool:
        truth_values = ('yes', 'true', '1')
        false_values = ('no', 'false', '0')
        if value.lower() not in truth_values and value.lower() not in false_values:
            raise EnvironmentError(f'For setting "{name}" use one of {truth_values} or {false_values}')
        return value.lower() in truth_values

    return cast(value)
