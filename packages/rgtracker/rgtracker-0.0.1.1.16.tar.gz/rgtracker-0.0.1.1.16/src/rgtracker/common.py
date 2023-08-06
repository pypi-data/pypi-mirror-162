from redisgears import executeCommand as execute
from redisgears import log
import json
from datetime import datetime, timedelta
from enum import Enum, IntEnum, unique

NAME = "TRACKER"


def tracker_log(msg, prefix=f'{NAME} - ', log_level='notice'):
    msg = prefix + msg
    log(msg, level=log_level)


def tracker_debug(msg):
    tracker_log(msg, log_level='debug')


# from utils import Type, Dimension, RedisNC, Metric, create_key_name, parse_key_name, round_time

@unique
class RedisNC(IntEnum):
    TYPE = 0,
    NAME = 1,
    DIMENSION = 2,
    RECORD_ID = 3,
    TS = 4,
    METRIC = 5


@unique
class Type(Enum):
    STREAM = 'ST'
    HASH = 'H'
    JSON = 'J'
    INDEX = 'I'
    TIMESERIES = 'TS'
    BLOOM = 'B'
    SORTEDSET = 'SS'
    SET = 'S'
    LIST = 'L'
    CHANNEL = 'C'
    CMS = 'CMS'
    HLL = 'HLL'


@unique
class Dimension(Enum):
    WEBSITE = 'W'
    SECTION = 'S'
    PAGE = 'P'
    DEVICE = 'D'
    AUDIO = 'A'
    VIDEO = 'V'
    PODCAST = 'PC'
    METRIC = 'M'


@unique
class Metric(Enum):
    PAGEVIEWS = 'PG'
    DEVICES = 'D'
    UNIQUE_DEVICES = 'UD'


def create_key_name(type, name='', dimension='', record_id='', ts='', metric=''):
    return f'{type}:{name}:{dimension}:{record_id}:{ts}:{metric}'


def parse_key_name(key):
    def check_none(check_value):
        if check_value == '':
            return None
        else:
            return check_value

    key_split = key.split(':')
    type = check_none(key_split[RedisNC.TYPE])
    name = check_none(key_split[RedisNC.NAME])
    dimension = check_none(key_split[RedisNC.DIMENSION])
    record_id = check_none(key_split[RedisNC.RECORD_ID])
    ts = check_none(key_split[RedisNC.TS])
    metric = check_none(key_split[RedisNC.METRIC])

    return {
        'type': type,
        'name': name,
        'dimension': dimension,
        'record_id': record_id,
        'ts': ts,
        'metric': metric
    }


def round_time(dt=None, round_to=60):
    if dt is None: dt = datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rouding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rouding - seconds, -dt.microsecond)


def convert_list_to_dict(x):
    it = iter(x)
    res_dct = dict(zip(it, it))
    return res_dct


def get_ts(ts, ts_arr):
    if len(ts.split('_')) > 1:
        return f'{ts_arr[0].get("ts").split("_")[0]}_{ts_arr[-1].get("ts").split("_")[-1]}'
    else:
        return f'{ts_arr[0].get("ts")}_{ts_arr[-1].get("ts")}'


def get_ts_df(ts, ts_arr):
    if len(ts.split('_')) > 1:
        return f'{ts_arr.iloc[0].split("_")[0]}_{ts_arr.iloc[-1].split("_")[-1]}'
    else:
        return f'{ts_arr.iloc[0]}_{ts_arr.iloc[-1]}'


def registration_arr_to_dict(registration, depth):
    if depth >= 2:
        return registration
    if type(registration) is not list:
        return registration
    d = {}
    for i in range(0, len(registration), 2):
        d[registration[i]] = registration_arr_to_dict(registration[i + 1], depth + 1)
    return d


def compare_versions(v1, v2):
    # None version is less then all version
    if v1 is None:
        return -1
    if v2 is None:
        return 1

    if v1 == "99.99.99":
        return 1
    if v2 == "99.99.99":
        return -1

    v1_major, v1_minor, v1_patch = v1.split(".")
    v2_major, v2_minor, v2_patch = v2.split(".")

    if int(v1_major) > int(v2_major):
        return 1
    elif int(v1_major) < int(v2_major):
        return -1

    if int(v1_minor) > int(v2_minor):
        return 1
    elif int(v1_minor) < int(v2_minor):
        return -1

    if int(v1_patch) > int(v2_patch):
        return 1
    elif int(v1_patch) < int(v2_patch):
        return -1

    return 0


def unregister_old_versions(name, version):
    tracker_log(f"Unregister old version of {name}")
    registrations = execute("RG.DUMPREGISTRATIONS")
    for registration in registrations:
        registration_dict = registration_arr_to_dict(registration, 0)
        desc_str = registration_dict["desc"]
        try:
            desc = json.loads(desc_str)
        except Exception as e:
            continue
        if "name" in desc.keys() and name in desc["name"]:
            tracker_log(
                "Version auto upgrade is not atomic, make sure to use it when is not traffic to the database (otherwise you might lose events).",
                log_level="warning"
            )
            if "version" not in desc.keys():
                execute("RG.UNREGISTER", registration_dict["id"])
                tracker_log(f"Unregister {registration_dict['ID']}")
                continue
            v = desc["version"]
            if compare_versions(version, v) > 0:
                execute("RG.UNREGITSTER", registration_dict["id"])
                tracker_log(f"Unregistered {registration_dict['id']}")
            else:
                raise Exception(
                    "Found a version which is greater or equals current version, aborting."
                )
    tracker_log("Unregistered old versions.")
