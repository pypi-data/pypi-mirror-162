from rgtracker.record import *
from rgtracker.tracker import *
from rgtracker.common import *
from rgtracker.website import *
from rgtracker.section import *
from rgtracker.page import *
from rgtracker.device import *
from rgtracker.uniquedevices import *
from redisgears import log


# Unique Devices Rotation Jobs - HLL
unique_devices_rotate_jobs = [
    # Run the job every 5 minutes to rotate 5 key of 1 minute each.
    # Expire new merged key after 30 minutes (keep 6 merged keys of 5 minutes each)
    {
        'input_stream_name': create_key_name(Type.STREAM.value, '1MINUTE', '', '', '', Metric.UNIQUE_DEVICES.value),
        'dimension': Dimension.WEBSITE.value,
        'number_of_rotated_keys': 5,
        'write_to_ts': True,
        'timeseries_name': '5MINUTES',
        'key_expire_duration_sc': 1820, # keep 6 keys -> merged key expire 30 minutes later
        'batch_size': 10000,
        'batch_interval_ms': 300000,
        'output_stream_name': create_key_name(Type.STREAM.value, '5MINUTES', '', '', '', Metric.UNIQUE_DEVICES.value)
    },
    # Run the job every 10 minutes to rotate 2 key of 5 minutes each.
    # Expire new merged key after 60 minutes (keep 6 merged keys of 10 minutes each)
    {
        'input_stream_name': create_key_name(Type.STREAM.value, '5MINUTES', '', '', '', Metric.UNIQUE_DEVICES.value),
        'dimension': Dimension.WEBSITE.value,
        'number_of_rotated_keys': 2,
        'write_to_ts': False,
        'timeseries_name': '',
        'key_expire_duration_sc': 3620, # keep 6 keys -> merged key expire 60 minutes later
        'batch_size': 10000,
        'batch_interval_ms': 600000,
        'output_stream_name': create_key_name(Type.STREAM.value, '10MINUTES', '', '', '', Metric.UNIQUE_DEVICES.value)
    },
    # Run the job every 60 minutes to rotate 6 key of 10 minutes each.
    # Expire new merged key after 24 hours (keep 24 merged keys of 1 hour each)
    {
        'input_stream_name': create_key_name(Type.STREAM.value, '10MINUTES', '', '', '', Metric.UNIQUE_DEVICES.value),
        'dimension': Dimension.WEBSITE.value,
        'number_of_rotated_keys': 6,
        'write_to_ts': False,
        'timeseries_name': '',
        'key_expire_duration_sc': 86420, # keep 6 keys -> merged key expire 60 minutes later
        'batch_size': 10000,
        'batch_interval_ms': 3600000,
        'output_stream_name': create_key_name(Type.STREAM.value, '1HOUR', '', '', '', Metric.UNIQUE_DEVICES.value)
    },
]
for job in unique_devices_rotate_jobs:
    GB("StreamReader"). \
        filter(lambda record: extract(record, dimension=job.get('dimension'))). \
        aggregateby(lambda e: e['value']['id'],
                    [],
                    lambda k, a, r: a + [r['value']],
                    lambda k, a, r: a + r). \
        map(lambda record: transform(record, job.get('number_of_rotated_keys'))). \
        foreach(lambda x: log(f'Megastorm Record: {x}')). \
        foreach(lambda record: load(
            record,
            job.get('dimension'),
            job.get('write_to_ts'),
            job.get('timeseries_name'),
            job.get('key_expire_duration_sc'),
            job.get('input_stream_name'),
            job.get('output_stream_name')
        )). \
        register(
        prefix=job.get('input_stream_name'),
        convertToStr=True,
        collect=True,
        onFailedPolicy='abort',
        onFailedRetryInterval=1,
        batch=job.get('batch_size'),
        duration=job.get('batch_interval_ms'),
        trimStream=False)
