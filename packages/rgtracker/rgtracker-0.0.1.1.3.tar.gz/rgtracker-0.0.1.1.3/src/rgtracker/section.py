from rgtracker.common import *
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar
from redisgears import executeCommand as execute
from redisgears import log


@dataclass
class Section:
    id: str
    pretty_name: str = None
    levels: dict = None
    last_visited: str = None
    dimension_key: field(init=False) = None
    dimension_ts_key: field(init=False) = None
    metric_pageviews_key: field(init=False) = None
    metric_devices_key: field(init=False) = None
    metric_unique_device_key: field(init=False) = None
    cms_width: ClassVar[int] = 2000
    cms_depth: ClassVar[int] = 5

    def __post_init__(self):
        self.dimension_key = f'{Type.JSON.value}::{Dimension.SECTION.value}:{self.id}::'
        if len(self.last_visited.split('_')) > 1:
            self.dimension_ts_key = f'{Type.JSON.value}::{Dimension.SECTION.value}:{self.id}:{self.last_visited}:'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{self.last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_devices_key = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{self.last_visited}:{Metric.DEVICES.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{self.last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ len(last_visited) > 1  \n{self.dimension_key}\n{self.metric_devices_key}\n{self.metric_devices_key}\n{self.metric_unique_device_key}')
        else:
            # Fixme: subtract and rounded time from timestamp
            dt = datetime.fromtimestamp(int(self.last_visited) / 1000) if self.last_visited is not None else None
            rounded_last_visited = int(round_time(dt).timestamp() * 1000)
            self.dimension_ts_key = f'{Type.JSON.value}::{Dimension.SECTION.value}:{self.id}:{rounded_last_visited}:'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{rounded_last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_devices_key = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{rounded_last_visited}:{Metric.DEVICES.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{rounded_last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ \n{self.dimension_key}\n{self.metric_devices_key}\n{self.metric_devices_key}\n{self.metric_unique_device_key}')

    def create(self, website):
        execute('SADD', Dimension.SECTION.value, f'{self.id}:{self.pretty_name}')
        # log(f'SADD {Dimension.SECTION.value} {self.id}:{self.pretty_name}')
        l = []
        [l.extend([k, v]) for k, v in self.levels.items()]
        # it = iter(l)
        # levels = dict(zip(it, it))
        levels = convert_list_to_dict(l)
        execute('JSON.SET', self.dimension_key, '.', json.dumps({
            'id': self.id,
            'website': {
                'id': website.id,
                'name': website.name
            },
            'pretty_name': self.pretty_name,
            # 'levels': # Todo: *l -> dict
            **levels,
            # Optional Pages
            'pages': [],
            'last_visited': self.last_visited,
        }))
        log(f'JSON.SET {self.dimension_key}')
        execute('JSON.ARRAPPEND', website.dimension_key, '$.sections', json.dumps({
            'id': self.id,
            'pretty_name': self.pretty_name,
            # **self.levels,
            'last_visited': int(self.last_visited)
        }))
        # log(f'JSON.ARRAPPEND {website.dimension_key} $.sections')

    def create_metrics(self, previous_keys=None):
        if previous_keys is None:
            try:
                execute('CMS.INITBYDIM', self.metric_pageviews_key, self.cms_width, self.cms_depth)
                # log(f'CMS.INITBYDIM {self.metric_pageviews_key} {self.cms_width} {self.cms_depth}')
            except Exception:
                # log(f'create_metrics: key {self.metric_pageviews_key} already exists')
                pass
            try:
                execute('CMS.INITBYDIM', self.metric_devices_key, self.cms_width, self.cms_depth)
                # log(f'CMS.INITBYDIM {self.metric_devices_key} {self.cms_width} {self.cms_depth}')
            except Exception:
                # log(f'create_metrics: key {self.metric_devices_key} already exists')
                pass
        else:
            try:
                execute('CMS.INITBYDIM', previous_keys.get('key_names').get('previous_pageviews_keys'), self.cms_width,
                        self.cms_depth)
                # log(f'CMS.INITBYDIM {previous_keys.get("key_names").get("previous_pageviews_keys")} {self.cms_width} {self.cms_depth}')
            except Exception:
                # log(f'create_metrics: key {previous_keys.get("key_names").get("previous_pageviews_keys")} already exists')
                pass
            try:
                execute('CMS.INITBYDIM', previous_keys.get('key_names').get('previous_devices_keys'), self.cms_width,
                        self.cms_depth)
                # log(f'CMS.INITBYDIM {previous_keys.get("key_names").get("previous_devices_keys")} {self.cms_width} {self.cms_depth}')
            except Exception:
                # log(f'create_metrics: key {previous_keys.get("key_names").get("previous_devices_keys")} already exists')
                pass

    def incr_metrics(self, page_id, device_id):
        execute('CMS.INCRBY', self.metric_pageviews_key, page_id, 1)
        # log(f'CMS.INCRBY {self.metric_pageviews_key} {page_id} {1}')
        execute('CMS.INCRBY', self.metric_devices_key, device_id, 1)
        # log(f'CMS.INCRBY {self.metric_devices_key} {device_id} {1}')
        execute('PFADD', self.metric_unique_device_key, device_id)
        # log(f'PFADD {self.metric_unique_device_key} {device_id}')

    def is_exists(self, key=None):
        if key is None:
            x = execute('EXISTS', self.dimension_key)
            # log(f'EXISTS {self.dimension_key} => {x}')
            return x
        else:
            x = execute('EXISTS', key)
            # log(f'EXISTS {key} => {x}')
            return x

    def has_metrics(self):
        x = execute('EXISTS', self.metric_pageviews_key)
        y = execute('EXISTS', self.metric_devices_key)
        z = execute('EXISTS', self.metric_unique_device_key)
        # log(f'EXISTS {self.metric_pageviews_key} => {x}')
        # log(f'EXISTS {self.metric_devices_key} => {y}')
        # log(f'EXISTS {self.metric_unique_device_key} => {z}')
        # log(f'EXISTS => {x + y + z}')
        return x + y + z

    def update_last_visited(self):
        execute('JSON.SET', self.dimension_key, '.last_visited', self.last_visited)
        # log(f'update_last_visited: JSON.SET {self.dimension_key} .last_visited {self.last_visited}')

    # Fixme: change method name
    def write_metadata(self, stream_name, previous_keys=None):
        if previous_keys is None:
            execute('XADD', stream_name, '*', 'dimension', Dimension.SECTION.value, 'key',
                    self.dimension_ts_key)
            # log(f'XADD {stream_name} * dimension {Dimension.SECTION.value} key {self.dimension_ts_key}')
        else:
            execute('XADD', stream_name, '*', 'dimension', Dimension.SECTION.value, 'key',
                    previous_keys.get("key_names").get("previous_pageviews_keys"))
            # log(f'XADD {stream_name} * dimension {Dimension.SECTION.value} key {previous_keys.get("key_names").get("previous_pageviews_keys")}')

            execute('XADD', stream_name, '*', 'dimension', Dimension.SECTION.value, 'key',
                    previous_keys.get("key_names").get("previous_devices_keys"))
            # log(f'XADD {stream_name} * dimension {Dimension.SECTION.value} key {previous_keys.get("key_names").get("previous_devices_keys")}')

            execute('XADD', stream_name, '*', 'dimension', Dimension.SECTION.value, 'key',
                    previous_keys.get("key_names").get("previous_unique_devices_keys"))
            # log(f'XADD {stream_name} * dimension {Dimension.SECTION.value} key {previous_keys.get("key_names").get("previous_unique_devices_keys")}')

    def write_metrics(self, timeseries_name, merged_key):
        pg_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.SECTION.value,
                                 record_id=self.id, metric=Metric.PAGEVIEWS.value)
        d_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.SECTION.value,
                                record_id=self.id, metric=Metric.DEVICES.value)
        u_d_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.SECTION.value,
                                  record_id=self.id, metric=Metric.UNIQUE_DEVICES.value)

        ts = merged_key.get('key_names').get('previous_key').split(':')[RedisNC.TS].split('_')[0]

        pageviews = execute('CMS.INFO', merged_key.get('key_names').get('previous_pageviews_keys'))[-1]
        devices = execute('CMS.INFO', merged_key.get('key_names').get('previous_devices_keys'))[-1]
        unique_devices = execute('PFCOUNT', merged_key.get('key_names').get('previous_unique_devices_keys'))

        section_info = \
            execute('FT.SEARCH', 'sections', f'@id:{{{self.id}}}', 'RETURN', '3', 'pretty_name', 'website_id',
                    'website_name')[-1][-1]

        execute('TS.ADD', pg_key, ts, pageviews, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension', Dimension.SECTION.value,
                Dimension.METRIC, Metric.PAGEVIEWS.value, 'section_id', self.id, *section_info[-1])
        log(f'TS.ADD {pg_key} {ts} {pageviews} ON_DUPLICATE LAST LABELS dimension {Dimension.SECTION.value} {Dimension.METRIC.value} {Metric.PAGEVIEWS.value} section_id {self.id} {section_info[-1]}')

        execute('TS.ADD', d_key, ts, devices, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension', Dimension.SECTION.value,
                Dimension.METRIC, Metric.DEVICES.value, 'section_id', self.id, *section_info[-1])
        # log(f'TS.ADD {d_key} {ts} {devices} ON_DUPLICATE LAST LABELS dimension {Dimension.SECTION.value} {Dimension.METRIC.value} {Metric.DEVICES.value} section_id {self.id} {section_info[-1]}')

        execute('TS.ADD', u_d_key, ts, unique_devices, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension',
                Dimension.SECTION.value, Dimension.METRIC, Metric.DEVICES.value, 'section_id', self.id,
                *section_info[-1])
        # log(f'TS.ADD {u_d_key} {ts} {unique_devices} ON_DUPLICATE LAST LABELS dimension {Dimension.SECTION.value} {Dimension.METRIC.value} {Metric.UNIQUE_DEVICES.value} section_id {self.id} {section_info[-1]}')

    def get_previous_ts(self, delta, minutes=True, hours=False):
        last_visited = self.last_visited.split('_')
        if len(last_visited) > 1:
            first_dt = datetime.fromtimestamp(int(last_visited[0]) / 1000)
            last_dt = datetime.fromtimestamp(int(last_visited[-1]) / 1000)
            prev_first_dt = None
            prev_last_dt = None
            if minutes:
                prev_first_dt = int((first_dt - timedelta(minutes=delta)).timestamp() * 1000)
                prev_last_dt = int((last_dt - timedelta(minutes=delta)).timestamp() * 1000)
            elif hours:
                prev_first_dt = int((first_dt - timedelta(hours=delta)).timestamp() * 1000)
                prev_last_dt = int((last_dt - timedelta(hours=delta)).timestamp() * 1000)
            # log(f'get_previous_ts: {prev_first_dt}_{prev_last_dt}')
            return f'{prev_first_dt}_{prev_last_dt}'
        else:
            if minutes:
                x = int((datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(
                    minutes=delta)).timestamp() * 1000)
                # log(f'get_previous_ts => {x}')
                return x
            elif hours:
                x = int(
                    (datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(hours=delta)).timestamp() * 1000)
                # log(f'get_previous_ts => {x}')
                return x

    def get_previous_key(self, previous_ts):
        x = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{previous_ts}:{Metric.PAGEVIEWS.value}'
        # log(f'get_previous_key => {x}')
        return x

    def create_previous_keys(self, minutes=True, hours=False):
        prev_pg_keys = []
        prev_devices_keys = []
        prev_unique_devices_keys = []
        for index in range(0, 6):
            prev_ts = None
            if minutes:
                prev_ts = int((datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(
                    minutes=index)).timestamp() * 1000)
            elif hours:
                prev_ts = int(
                    (datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(hours=index)).timestamp() * 1000)
            prev_pg_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{prev_ts}:{Metric.PAGEVIEWS.value}')
            prev_devices_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{prev_ts}:{Metric.DEVICES.value}')
            prev_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{prev_ts}:{Metric.UNIQUE_DEVICES.value}')

        first_ts = prev_pg_keys[0].split(':')[RedisNC.TS]
        last_ts = prev_pg_keys[-1].split(':')[RedisNC.TS]
        merge_pg_key_name = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{first_ts}_{last_ts}:{Metric.PAGEVIEWS.value}'
        merge_devices_key_name = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{first_ts}_{last_ts}:{Metric.DEVICES.value}'
        merge_unique_devices_key_name = f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{first_ts}_{last_ts}:{Metric.UNIQUE_DEVICES.value}'

        x = {
            'key_names': {
                'previous_key': f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{first_ts}_{last_ts}:',
                'previous_pageviews_keys': merge_pg_key_name,
                'previous_devices_keys': merge_devices_key_name,
                'previous_unique_devices_keys': merge_unique_devices_key_name,
            },
            'key_values': {
                'previous_pageviews_keys': prev_pg_keys,
                'previous_devices_keys': prev_devices_keys,
                'previous_unique_devices_keys': prev_unique_devices_keys,
            }
        }
        log(f'create_previous_keys => {x}')
        return x

    @staticmethod
    def merge_metrics(previous_keys):
        execute('CMS.MERGE', previous_keys.get('key_names').get('previous_pageviews_keys'),
                len(previous_keys.get('key_values').get('previous_pageviews_keys')),
                *previous_keys.get('key_values').get('previous_pageviews_keys'))
        # log(f'CMS.MERGE {previous_keys.get("key_names").get("previous_pageviews_keys")} {len(previous_keys.get("key_values").get("previous_pageviews_keys"))} {previous_keys.get("key_values").get("previous_pageviews_keys")}')

        execute('CMS.MERGE', previous_keys.get('key_names').get('previous_devices_keys'),
                len(previous_keys.get('key_values').get('previous_devices_keys')),
                *previous_keys.get('key_values').get('previous_devices_keys'))
        # log(f'CMS.MERGE {previous_keys.get("key_names").get("previous_devices_keys")} {len(previous_keys.get("key_values").get("previous_devices_keys"))} {previous_keys.get("key_values").get("previous_devices_keys")}')

        execute('PFMERGE', previous_keys.get('key_names').get('previous_unique_devices_keys'),
                *previous_keys.get('key_values').get('previous_unique_devices_keys'))
        # log(f'PFMERGE {previous_keys.get("key_names").get("previous_unique_devices_keys")} {previous_keys.get("key_values").get("previous_unique_devices_keys")}')

    def create_previous_keys_concat(self, range, minutes=True, hours=False):
        last_visited = self.last_visited.split('_')
        prev_pg_keys = []
        prev_devices_keys = []
        prev_unique_devices_keys = []
        for index in range:
            prev_f_ts = None
            prev_l_ts = None
            if minutes:
                prev_f_ts = int(
                    (datetime.fromtimestamp(int(last_visited[0]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
                prev_l_ts = int((datetime.fromtimestamp(int(last_visited[-1]) / 1000) - timedelta(
                    minutes=index)).timestamp() * 1000)
            elif hours:
                prev_f_ts = int(
                    (datetime.fromtimestamp(int(last_visited[0]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
                prev_l_ts = int(
                    (datetime.fromtimestamp(int(last_visited[-1]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
            prev_pg_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.PAGEVIEWS.value}')
            prev_devices_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.DEVICES.value}')
            prev_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.UNIQUE_DEVICES.value}')

        last_merge_ts = prev_pg_keys[-1].split(":")[RedisNC.TS].split("_")[-1]
        merge_pg_key_name = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.PAGEVIEWS.value}'
        merge_devices_key_name = f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.DEVICES.value}'
        merge_unique_devices_key_name = f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.UNIQUE_DEVICES.value}'

        x = {
            'key_names': {
                'current_key': f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{last_visited[0]}_{last_visited[-1]}:',
                'previous_key': f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:',
                'previous_pageviews_keys': merge_pg_key_name,
                'previous_devices_keys': merge_devices_key_name,
                'previous_unique_devices_keys': merge_unique_devices_key_name,
            },
            'key_values': {
                'previous_pageviews_keys': prev_pg_keys,
                'previous_devices_keys': prev_devices_keys,
                'previous_unique_devices_keys': prev_unique_devices_keys,
            }
        }
        return x

    @staticmethod
    def delete_previous_key(previous_keys):
        execute('DEL', *previous_keys.get('key_values').get('previous_pageviews_keys'))
        # log(f'delete_previous_key: DEL {previous_keys.get("key_values").get("previous_pageviews_keys")}')

        execute('DEL', *previous_keys.get('key_values').get('previous_devices_keys'))
        # log(f'delete_previous_key: DEL {previous_keys.get("key_values").get("previous_devices_keys")}')

        execute('DEL', *previous_keys.get('key_values').get('previous_unique_devices_keys'))
        # log(f'delete_previous_key: DEL {previous_keys.get("key_values").get("previous_unique_devices_keys")}')

    def delete_previous_key_concat(self, previous_keys, delta, range, minutes=True, hours=False):
        ts = previous_keys.get('key_names').get('current_key').split(':')[RedisNC.TS].split('_')
        del_pg_keys = []
        del_devices_keys = []
        del_unique_devices_keys = []
        for index in range:
            first = None
            last = None
            if minutes:
                first = int((datetime.fromtimestamp(int(ts[0]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
                last = int((datetime.fromtimestamp(int(ts[-1]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
            elif hours:
                first = int((datetime.fromtimestamp(int(ts[0]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
                last = int((datetime.fromtimestamp(int(ts[-1]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
            del_pg_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{first}_{last}:{Metric.PAGEVIEWS.value}')
            del_devices_keys.append(
                f'{Type.CMS.value}::{Dimension.SECTION.value}:{self.id}:{first}_{last}:{Metric.DEVICES.value}')
            del_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.SECTION.value}:{self.id}:{first}_{last}:{Metric.UNIQUE_DEVICES.value}')

        execute('DEL', *del_pg_keys)
        log(f'DEL {del_pg_keys}')
        execute('DEL', *del_devices_keys)
        log(f'DEL {del_devices_keys}')
        execute('DEL', *del_unique_devices_keys)
        log(f'DEL {del_unique_devices_keys}')
