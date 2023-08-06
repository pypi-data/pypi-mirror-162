from rgtracker.common import *
import math
import pandas as pd
from redisgears import executeCommand as execute
from redisgears import log


def extract(record, dimension):
    return record['value']['dimension'] == dimension


def transform(records, number_of_rotated_keys):
    log(f'MegaStorm - Transform -> {records.get("key")} {len(records.get("value"))}')

    df = pd.DataFrame(records.get("value"))
    df_sort = df.sort_values('ts')

    expected_rows = number_of_rotated_keys
    chunks = math.floor(len(df_sort['ts']) / expected_rows + 1)
    i = 0
    j = expected_rows
    results = {
        'merge': [],
        'reinject': []
    }
    for x in range(chunks):
        df_sliced = df_sort[i:j]
        if df_sliced.shape[0] >= number_of_rotated_keys:
            results.get('merge').append({
                'name': create_key_name(
                    Type.HLL.value,
                    '',
                    df_sliced["dimension"].iloc[0],
                    '',
                    get_ts_df(df_sliced["ts"].iloc[0], df_sliced["ts"]),
                    Metric.UNIQUE_DEVICES.value
                ),
                'keys': [create_key_name(Type.HLL.value, '', row[0], '', row[1], Metric.UNIQUE_DEVICES.value) for row in
                         zip(df_sliced['dimension'], df_sliced['ts'])]
            })
        else:
            [results.get('reinject').append({
                'dimension': row[0],
                'ts': row[1],
                'id': row[2]
            }) for row in zip(df_sliced['dimension'], df_sliced['ts'], df_sliced['id'])]

        i += expected_rows
        j += expected_rows

    return results


def load(records, dimension, write_to_ts, timeseries_name, key_expire_duration_sc, reinject_stream_name,
         output_stream_name):
    def get_ts(ts):
        if len(ts.split('_')) > 1:
            return ts.split("_")[-1]
        else:
            return ts

    for hll_reinject in records.get('reinject'):
        execute('XADD', reinject_stream_name, '*', 'id', hll_reinject.get('id'), 'dimension', hll_reinject.get('dimension'), 'ts', hll_reinject.get('ts'))

    for hll_merge in records.get("merge"):
        if execute('EXISTS', hll_merge.get('name')) != 1:
            execute('PFMERGE', hll_merge.get('name'), *hll_merge.get('keys'))

            parsed_key_name = parse_key_name(hll_merge.get('name'))

            if write_to_ts:
                unique_devices = execute('CMS.QUERY', hll_merge.get('name'), id)
                index_name = create_key_name(
                    type=Type.INDEX.value,
                    name='',
                    dimension=dimension,
                    record_id='',
                    ts='',
                    metric='')
                timeseries_key_name = create_key_name(
                    type=Type.TIMESERIES.value,
                    name=timeseries_name,
                    dimension=dimension,
                    record_id=hll_merge.get('id'),
                    metric=Metric.UNIQUE_DEVICES.value)

                if dimension == Dimension.WEBSITE.value:
                    record_infos = execute('FT.SEARCH', index_name, f'@id:{{{hll_merge.get("id")}}}', 'RETURN', '1', 'name')[-1]
                    execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get('ts')), unique_devices,
                            'ON_DUPLICATE', 'LAST',
                            'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.UNIQUE_DEVICES.value,
                            'website_id', hll_merge.get('id'), *record_infos)
                elif dimension == Dimension.SECTION.value:
                    record_infos = execute('FT.SEARCH', index_name, f'@id:{{{hll_merge.get("id")}}}', 'RETURN', '3',
                                           'pretty_name', 'website_id', 'website_name')[-1][-1]
                    execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), unique_devices,
                            'ON_DUPLICATE', 'LAST',
                            'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.UNIQUE_DEVICES.value,
                            'section_id', hll_merge.get('id'), *record_infos)
                elif dimension == Dimension.PAGE.value:
                    record_infos = execute('FT.SEARCH', index_name, f'@id:{{{hll_merge.get("id")}}}', 'RETURN', '5',
                                           'website_id', 'website_name', 'section_id',
                                           'section_pretty_name', 'article_id')[-1][-1]
                    execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), unique_devices,
                            'ON_DUPLICATE', 'LAST',
                            'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.UNIQUE_DEVICES.value,
                            'page_id', hll_merge.get('id'), *record_infos)


            execute('XADD', output_stream_name, '*', 'dimension', dimension, 'id', hll_merge.get('id'), 'ts', parsed_key_name.get('ts'))

            # execute('EXPIRE', hll_merge.get('name'), key_expire_duration_sc)
