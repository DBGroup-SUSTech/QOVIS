from enum import Enum


class AlgoStatus(Enum):
    INIT = 'init'
    TIMEOUT = 'timeout'
    FAILED = 'failed'
    SUCCESS = 'success'
