from redisgears import log

NAME = "TRACKER"


def tracker_log(msg, prefix=f'{NAME} - ', log_level='notice'):
    msg = prefix + msg
    log(msg, level=log_level)


def tracker_debug(msg):
    tracker_log(msg, log_level='debug')
