from rgtracker.common import *
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar
from redisgears import executeCommand as execute
from redisgears import log


@dataclass
class Website:
    id: str
    name: str = None
    last_visited: str = None
    dimension_key: field(init=False) = None
    dimension_ts_key: field(init=False) = None
    metric_pageviews_key: field(init=False) = None
    # metric_devices_key: field(init=False) = None
    metric_unique_device_key: field(init=False) = None
    cms_width: ClassVar[int] = 2000
    cms_depth: ClassVar[int] = 5

    def __post_init__(self):
        self.dimension_key = f'{Type.JSON.value}::{Dimension.WEBSITE.value}:{self.id}::'
        if len(self.last_visited.split('_')) > 1:
            # self.dimension_ts_key = f'{Type.JSON.value}::{Dimension.WEBSITE.value}:{self.id}:{self.last_visited}:'
            self.dimension_ts_key = f'::{Dimension.WEBSITE.value}:{self.id}:{self.last_visited}:'
            # self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{self.last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{self.last_visited}:{Metric.PAGEVIEWS.value}'
            # self.metric_devices_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{self.last_visited}:{Metric.DEVICES.value}'
            # self.metric_devices_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{self.last_visited}:{Metric.DEVICES.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{self.last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ len(last_visited) > 1  \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_devices_key}\n{self.metric_unique_device_key}')
            log(f'__post_init__ len(last_visited) > 1  \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_unique_device_key}')
        else:
            dt = datetime.fromtimestamp(int(self.last_visited) / 1000) if self.last_visited is not None else None
            rounded_last_visited = int(round_time(dt).timestamp() * 1000)
            # self.dimension_ts_key = f'{Type.JSON.value}::{Dimension.WEBSITE.value}:{self.id}:{rounded_last_visited}:'
            self.dimension_ts_key = f'::{Dimension.WEBSITE.value}:{self.id}:{rounded_last_visited}:'
            # self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{rounded_last_visited}:{Metric.PAGEVIEWS.value}'
            self.metric_pageviews_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{rounded_last_visited}:{Metric.PAGEVIEWS.value}'
            # self.metric_devices_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{rounded_last_visited}:{Metric.DEVICES.value}'
            # self.metric_devices_key = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{rounded_last_visited}:{Metric.DEVICES.value}'
            self.metric_unique_device_key = f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{rounded_last_visited}:{Metric.UNIQUE_DEVICES.value}'
            # log(f'__post_init__ \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_devices_key}\n{self.metric_unique_device_key}')
            # log(f'__post_init__ \n{self.dimension_key}\n{self.metric_pageviews_key}\n{self.metric_unique_device_key}')

    def create(self):
        execute('SADD', Dimension.WEBSITE.value, f'{self.id}:{self.name}')
        log(f'SADD websites {self.name}:{self.id}')
        execute('JSON.SET', self.dimension_key, '.', json.dumps({
            'id': self.id,
            'name': self.name,
            'last_visited': self.last_visited,
            'sections': [],
            'pages': []
        }))
        log(f'JSON.SET {self.dimension_key}')

    def create_metrics(self, previous_keys=None):
        if previous_keys is None:
            try:
                execute('CMS.INITBYDIM', self.metric_pageviews_key, self.cms_width, self.cms_depth)
                # log(f'CMS.INITBYDIM {self.metric_pageviews_key} {self.cms_width} {self.cms_depth}')

            except Exception:
                # log(f'S-create_metrics: key {self.metric_pageviews_key} already exists')
                pass
            # try:
            #     execute('CMS.INITBYDIM', self.metric_devices_key, self.cms_width, self.cms_depth)
            #     log(f'CMS.INITBYDIM {self.metric_devices_key} {self.cms_width} {self.cms_depth}')
            # except Exception:
            #     log(f'S-create_metrics: key {self.metric_devices_key} already exists')
            #     pass
        else:
            try:
                execute('CMS.INITBYDIM', previous_keys.get('key_names').get('previous_pageviews_keys'), self.cms_width,
                        self.cms_depth)
                log(f'CMS.INITBYDIM {previous_keys.get("key_names").get("previous_pageviews_keys")} {self.cms_width} {self.cms_depth}')
            except Exception:
                log(f'S-create_metrics: key {previous_keys.get("key_names").get("previous_pageviews_keys")} already exists')
                pass
            # try:
            #     execute('CMS.INITBYDIM', previous_keys.get('key_names').get('previous_devices_keys'), self.cms_width,
            #             self.cms_depth)
            #     log(f'CMS.INITBYDIM {previous_keys.get("key_names").get("previous_devices_keys")} {self.cms_width} {self.cms_depth}')
            # except Exception:
            #     log(f'S-create_metrics: key {previous_keys.get("key_names").get("previous_devices_keys")} already exists')
            #     pass

    def incr_metrics(self, page_id, device_id):
        # execute('CMS.INCRBY', self.metric_pageviews_key, page_id, 1)
        # log(f'CMS.INCRBY {self.metric_pageviews_key} {page_id} {1}')
        execute('CMS.INCRBY', self.metric_pageviews_key, self.id, 1)
        # log(f'CMS.INCRBY {self.metric_pageviews_key} {self.id} {1}')

        # execute('CMS.INCRBY', self.metric_devices_key, device_id, 1)
        # log(f'CMS.INCRBY {self.metric_devices_key} {device_id} {1}')
        # execute('CMS.INCRBY', self.metric_devices_key, self.id, 1)
        # log(f'CMS.INCRBY {self.metric_devices_key} {self.id} {1}')

        execute('PFADD', self.metric_unique_device_key, device_id)
        # log(f'PFADD {self.metric_unique_device_key} {device_id}')

    def expire_metrics(self):
        # Todo: EXPIRE params
        execute('EXPIRE', self.metric_pageviews_key, 720)
        execute('EXPIRE', self.metric_unique_device_key, 720)

    @staticmethod
    def merge_metrics(previous_keys):
        log(f'Try to -> CMS.MERGE {previous_keys.get("key_names").get("previous_pageviews_keys")} {len(previous_keys.get("key_values").get("previous_pageviews_keys"))} {previous_keys.get("key_values").get("previous_pageviews_keys")}')

        execute('CMS.MERGE', previous_keys.get('key_names').get('previous_pageviews_keys'),
                len(previous_keys.get('key_values').get('previous_pageviews_keys')),
                *previous_keys.get('key_values').get('previous_pageviews_keys'))
        log(f'CMS.MERGE {previous_keys.get("key_names").get("previous_pageviews_keys")} {len(previous_keys.get("key_values").get("previous_pageviews_keys"))} {previous_keys.get("key_values").get("previous_pageviews_keys")}')

        # log(f'TRY TOO -> CMS.MERGE {previous_keys.get("key_names").get("previous_devices_keys")} ')
        # log(f'TRY TOO -> {len(previous_keys.get("key_values").get("previous_devices_keys"))}')
        # log(f'TRY TOO -> {previous_keys.get("key_values").get("previous_devices_keys")}')
        # execute('CMS.MERGE', previous_keys.get('key_names').get('previous_devices_keys'),
        #         len(previous_keys.get('key_values').get('previous_devices_keys')),
        #         *previous_keys.get('key_values').get('previous_devices_keys'))
        # log(f'CMS.MERGE {previous_keys.get("key_names").get("previous_devices_keys")} {len(previous_keys.get("key_values").get("previous_devices_keys"))} {previous_keys.get("key_values").get("previous_devices_keys")}')

        execute('PFMERGE', previous_keys.get('key_names').get('previous_unique_devices_keys'),
                *previous_keys.get('key_values').get('previous_unique_devices_keys'))
        log(f'PFMERGE {previous_keys.get("key_names").get("previous_unique_devices_keys")} {previous_keys.get("key_values").get("previous_unique_devices_keys")}')

    def is_exists(self, key=None):
        if key is None:
            x = execute('EXISTS', self.dimension_key)
            # log(f'EXISTS {self.dimension_key} => {x}')
            return x
        else:
            x = execute('EXISTS', key)
            log(f'EXISTS prev-{self.id}-{key} => {x}')
            return x

    def has_metrics(self):
        # Todo: check if all metrics exists?
        x = execute('EXISTS', self.metric_pageviews_key)
        # y = execute('EXISTS', self.metric_devices_key)
        z = execute('EXISTS', self.metric_unique_device_key)
        # log(f'EXISTS {self.metric_pageviews_key} => {x}')
        # # log(f'EXISTS {self.metric_devices_key} => {y}')
        # log(f'EXISTS {self.metric_unique_device_key} => {z}')
        # # log(f'EXISTS => {x + y + z}')
        # log(f'EXISTS => {x + z}')
        # # return x + y + z
        return x + z

    def update_last_visited(self):
        execute('JSON.SET', self.dimension_key, '.last_visited', self.last_visited)
        # log(f'update_last_visited: JSON.SET {self.dimension_key} .last_visited {self.last_visited}')

    # Fixme: change method name
    def write_metadata(self, stream_names, previous_keys=None):
        if previous_keys is None:

            parsed_key = parse_key_name(self.dimension_ts_key)

            execute('XADD', stream_names.get('pageviews'), '*', 'dimension', Dimension.WEBSITE.value, 'id', self.id, 'ts',
                    parsed_key.get('ts'))

            execute('XADD', stream_names.get('unique_devices'), '*', 'dimension', Dimension.WEBSITE.value, 'id', self.id, 'ts',
                    parsed_key.get('ts'))
        # else:
        #     execute('XADD', stream_name, '*', 'dimension', Dimension.WEBSITE.value, 'key',
        #             previous_keys.get("key_names").get("previous_pageviews_keys"))
        #     log(f'XADD {stream_name} * dimension {Dimension.WEBSITE.value} key {previous_keys.get("key_names").get("previous_pageviews_keys")}')
        #
        #     # execute('XADD', stream_name, '*', 'dimension', Dimension.WEBSITE.value, 'key',
        #     #         previous_keys.get("key_names").get("previous_devices_keys"))
        #     # log(f'XADD {stream_name} * dimension {Dimension.WEBSITE.value} key {previous_keys.get("key_names").get("previous_devices_keys")}')
        #
        #     execute('XADD', stream_name, '*', 'dimension', Dimension.WEBSITE.value, 'key',
        #             previous_keys.get("key_names").get("previous_unique_devices_keys"))
        #     log(f'XADD {stream_name} * dimension {Dimension.WEBSITE.value} key {previous_keys.get("key_names").get("previous_unique_devices_keys")}')

    def write_metrics(self, timeseries_name, merged_key):
        pg_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.WEBSITE.value,
                                 record_id=self.id, metric=Metric.PAGEVIEWS.value)
        # d_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.WEBSITE.value,
        #                         record_id=self.id, metric=Metric.DEVICES.value)
        u_d_key = create_key_name(type=Type.TIMESERIES.value, name=timeseries_name, dimension=Dimension.WEBSITE.value,
                                  record_id=self.id, metric=Metric.UNIQUE_DEVICES.value)

        ts = merged_key.get('key_names').get('previous_key').split(':')[RedisNC.TS].split('_')[0]

        pageviews = execute('CMS.INFO', merged_key.get('key_names').get('previous_pageviews_keys'))[-1]
        # devices = execute('CMS.INFO', merged_key.get('key_names').get('previous_devices_keys'))[-1]
        unique_devices = execute('PFCOUNT', merged_key.get('key_names').get('previous_unique_devices_keys'))

        website_info = execute('FT.SEARCH', 'websites', f'@id:{{{self.id}}}', 'RETURN', '1', 'name')[-1]
        # website_info = convert_list_to_dict(website_info[-1])
        # website_info.get('name')

        execute('TS.ADD', pg_key, ts, pageviews, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension',
                Dimension.WEBSITE.value, Dimension.METRIC.value, Metric.PAGEVIEWS.value, 'website_id', self.id,
                *website_info)
        log(f'TS.ADD {pg_key} {ts} {pageviews} ON_DUPLICATE LAST LABELS dimension {Dimension.WEBSITE.value} {Dimension.METRIC.value} {Metric.PAGEVIEWS.value} website_id {self.id} {website_info}')

        # execute('TS.ADD', d_key, ts, devices, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension', Dimension.WEBSITE.value,
        #         Dimension.METRIC.value, Metric.PAGEVIEWS.value, 'website_id', self.id, *website_info)
        # log(f'TS.ADD {d_key} {ts} {devices} ON_DUPLICATE LAST LABELS dimension {Dimension.WEBSITE.value} {Dimension.METRIC.value} {Metric.DEVICES.value} website_id {self.id} {website_info}')

        execute('TS.ADD', u_d_key, ts, unique_devices, 'ON_DUPLICATE', 'LAST', 'LABELS', 'dimension',
                Dimension.WEBSITE.value, Dimension.METRIC.value, Metric.PAGEVIEWS.value, 'website_id', self.id,
                *website_info)
        log(f'TS.ADD {u_d_key} {ts} {unique_devices} ON_DUPLICATE LAST LABELS dimension {Dimension.WEBSITE.value} {Dimension.METRIC.value} {Metric.UNIQUE_DEVICES.value} website_id {self.id} {website_info}')

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
            log(f'get_previous_ts: {prev_first_dt}_{prev_last_dt}')
            return f'{prev_first_dt}_{prev_last_dt}'
        else:
            if minutes:
                x = int((datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(
                    minutes=delta)).timestamp() * 1000)
                log(f'get_previous_ts => {x}')
                return x
            elif hours:
                x = int(
                    (datetime.fromtimestamp(int(self.last_visited) / 1000) - timedelta(hours=delta)).timestamp() * 1000)
                log(f'get_previous_ts => {x}')
                return x

    def get_previous_key(self, previous_ts):
        # x = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{previous_ts}:{Metric.PAGEVIEWS.value}'
        x = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{previous_ts}:{Metric.PAGEVIEWS.value}'
        log(f'get_previous_key => {x} {self.id}')
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
            # prev_pg_keys.append(
            # f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_ts}:{Metric.PAGEVIEWS.value}')
            prev_pg_keys.append(
                f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{prev_ts}:{Metric.PAGEVIEWS.value}')
            # prev_devices_keys.append(
            #     f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_ts}:{Metric.DEVICES.value}')
            # prev_devices_keys.append(
            #     f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{prev_ts}:{Metric.DEVICES.value}')
            prev_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_ts}:{Metric.UNIQUE_DEVICES.value}')

        first_ts = prev_pg_keys[0].split(':')[RedisNC.TS]
        last_ts = prev_pg_keys[-1].split(':')[RedisNC.TS]
        # merge_pg_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{first_ts}_{last_ts}:{Metric.PAGEVIEWS.value}'
        merge_pg_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{first_ts}_{last_ts}:{Metric.PAGEVIEWS.value}'
        # merge_devices_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{first_ts}_{last_ts}:{Metric.DEVICES.value}'
        # merge_devices_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{first_ts}_{last_ts}:{Metric.DEVICES.value}'
        merge_unique_devices_key_name = f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{first_ts}_{last_ts}:{Metric.UNIQUE_DEVICES.value}'

        x = {
            'key_names': {
                # 'previous_key': f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{first_ts}_{last_ts}:',
                'previous_key': f'{Type.CMS.value}::{Dimension.WEBSITE.value}::{first_ts}_{last_ts}:',
                'previous_pageviews_keys': merge_pg_key_name,
                # 'previous_devices_keys': merge_devices_key_name,
                'previous_unique_devices_keys': merge_unique_devices_key_name,
            },
            'key_values': {
                'previous_pageviews_keys': prev_pg_keys,
                # 'previous_devices_keys': prev_devices_keys,
                'previous_unique_devices_keys': prev_unique_devices_keys,
            }
        }
        log(f'create_previous_keys => {x}')
        return x

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
                f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.PAGEVIEWS.value}')
            # prev_devices_keys.append(
            #     f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.DEVICES.value}')
            prev_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{prev_f_ts}_{prev_l_ts}:{Metric.UNIQUE_DEVICES.value}')

        last_merge_ts = prev_pg_keys[-1].split(":")[RedisNC.TS].split("_")[-1]
        merge_pg_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.PAGEVIEWS.value}'
        # merge_devices_key_name = f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.DEVICES.value}'
        merge_unique_devices_key_name = f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:{Metric.UNIQUE_DEVICES.value}'

        x = {
            'key_names': {
                'current_key': f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{last_visited[0]}_{last_visited[-1]}:',
                'previous_key': f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{last_visited[0]}_{last_merge_ts}:',
                'previous_pageviews_keys': merge_pg_key_name,
                # 'previous_devices_keys': merge_devices_key_name,
                'previous_unique_devices_keys': merge_unique_devices_key_name,
            },
            'key_values': {
                'previous_pageviews_keys': prev_pg_keys,
                'previous_devices_keys': prev_devices_keys,
                'previous_unique_devices_keys': prev_unique_devices_keys,
            }
        }
        log(f'create_previous_keys_concat => {x}')
        return x

    @staticmethod
    def delete_previous_key(previous_keys):
        execute('DEL', *previous_keys.get('key_values').get('previous_pageviews_keys'))
        log(f'DEL {previous_keys.get("key_values").get("previous_pageviews_keys")}')

        # execute('DEL', *previous_keys.get('key_values').get('previous_devices_keys'))
        # log(f'DEL {previous_keys.get("key_values").get("previous_devices_keys")}')

        execute('DEL', *previous_keys.get('key_values').get('previous_unique_devices_keys'))
        log(f'DEL {previous_keys.get("key_values").get("previous_unique_devices_keys")}')

    def delete_previous_key_concat(self, previous_keys, delta, range, minutes=True, hours=False):
        ts = previous_keys.get('key_names').get('current_key').split(':')[RedisNC.TS].split('_')
        del_pg_keys = []
        del_devices_keys = []
        del_unique_devices_keys = []
        for index in range:
            # first = int((datetime.fromtimestamp(int(ts[0]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
            # last = int((datetime.fromtimestamp(int(ts[-1]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
            first = None
            last = None
            if minutes:
                first = int((datetime.fromtimestamp(int(ts[0]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
                last = int((datetime.fromtimestamp(int(ts[-1]) / 1000) - timedelta(minutes=index)).timestamp() * 1000)
            elif hours:
                first = int((datetime.fromtimestamp(int(ts[0]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
                last = int((datetime.fromtimestamp(int(ts[-1]) / 1000) - timedelta(hours=index)).timestamp() * 1000)
            del_pg_keys.append(
                f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{first}_{last}:{Metric.PAGEVIEWS.value}')
            # del_devices_keys.append(
            #     f'{Type.CMS.value}::{Dimension.WEBSITE.value}:{self.id}:{first}_{last}:{Metric.DEVICES.value}')
            del_unique_devices_keys.append(
                f'{Type.HLL.value}::{Dimension.WEBSITE.value}:{self.id}:{first}_{last}:{Metric.UNIQUE_DEVICES.value}')

        execute('DEL', *del_pg_keys)
        log(f'DEL {del_pg_keys}')
        # execute('DEL', *del_devices_keys)
        # log(f'DEL {del_devices_keys}')
        execute('DEL', *del_unique_devices_keys)
        log(f'DEL {del_unique_devices_keys}')


def load_website(website, section, page, device, output_stream_names):
    if website.is_exists() != 1:
        website.create()
        website.create_metrics()
        website.incr_metrics(page_id=page.id, device_id=device.id)
        website.expire_metrics()
        website.update_last_visited()
        website.write_metadata(stream_names=output_stream_names)
    else:
        if website.has_metrics() < 2:
            website.create_metrics()
            website.incr_metrics(page_id=page.id, device_id=device.id)
            website.expire_metrics()
            website.update_last_visited()
            website.write_metadata(stream_names=output_stream_names)
        else:
            website.incr_metrics(page_id=page.id, device_id=device.id)
            website.update_last_visited()
