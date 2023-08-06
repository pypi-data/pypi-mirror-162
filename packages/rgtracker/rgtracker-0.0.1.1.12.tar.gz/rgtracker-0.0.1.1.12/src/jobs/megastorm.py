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
    {
        # 'input_stream_name': create_key_name(Type.STREAM.value, '1MINUTES', '', '', '', Metric.PAGEVIEWS.value),
        'input_stream_name': create_key_name(Type.STREAM.value, '1MINUTES'),
        'dimension': Dimension.WEBSITE.value,
        'number_of_rotated_keys': 5,
        'write_to_ts': True,
        'timeseries_name': '5MINUTES',
        'key_expire_duration_sc': 1820,
        'batch_size': 10000,
        'batch_interval_ms': 300000,
        # 'output_stream_name': create_key_name(Type.STREAM.value, '5MINUTES', '', '', '', Metric.UNIQUE_DEVICES.value)
        'output_stream_name': create_key_name(Type.STREAM.value, '5MINUTES')
    }
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
