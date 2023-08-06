from rgtracker.common import *
import math
import pandas as pd
from gearsclient import log, execute


def extract(record, dimension):
    return record['value']['dimension'] == dimension


def transform(records, number_of_rotated_keys):
    log(f'Transform -> {len(records)} {records}')
    df = pd.DataFrame(records)
    df_ts = df.drop_duplicates('ts').sort_values('ts')
    df_id = df['id'].drop_duplicates('id')['id']

    expected_rows = number_of_rotated_keys
    chunks = math.floor(len(df_ts['ts']) / expected_rows + 1)
    i = 0
    j = expected_rows
    results = {
        'id': df_id.values.tolist(),
        'merge': [],
        'reinject': []
    }
    for x in range(chunks):
        df_sliced = df_ts[i:j]
        if df_sliced.shape[0] >= number_of_rotated_keys:
            results.get('merge').append({
                'name': create_key_name(
                    Type.CMS.value,
                    '',
                    df_sliced["dimension"].iloc[0],
                    '',
                    # TS
                    # f'{df_sliced["ts"].iloc[0]}_{df_sliced["ts"].iloc[-1]}',
                    # OR
                    # f'{df_sliced["ts"].iloc[0].split("_")[0]}_{df_sliced["ts"].iloc[-1].split("_")[-1]}'
                    get_ts(df_sliced["ts"].iloc[0], df_sliced["ts"]),
                    Metric.PAGEVIEWS.value
                ),
                'keys': [{
                    'dimension': row[0],
                    'ts': row[1]
                } for row in zip(df_sliced['dimension'], df_sliced['ts'])]
            })
        else:
            [results.get('reinject').append({
                'dimension': row[0],
                'ts': row[1]
            }) for row in zip(df_sliced['dimension'], df_sliced['ts'])]

        i += expected_rows
        j += expected_rows

    return results


def load(records, dimension, write_to_ts, timeseries_name, key_expire_duration_sc, reinject_stream_name, output_stream_name):

    def get_ts(ts):
        if len(ts.split('_')) > 1:
            return ts.split("_")[-1]
        else:
            return ts

    for cms_merge in records.get("merge"):
        if execute('EXISTS', cms_merge.get('name')) != 1:
            execute('CMS.INITBYDIM', cms_merge.get('name'), 2000, 5)
            execute('CMS.MERGE', cms_merge.get('name'), len(cms_merge.get('keys')), *cms_merge.get('keys'))

            parsed_key_name = parse_key_name(cms_merge.get('name'))

            if write_to_ts:
                for id in records.get('id'):
                    pageviews = execute('CMS.QUERY', cms_merge.get('name'), id)[0]
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
                        record_id=id,
                        metric=Metric.PAGEVIEWS.value)

                    if dimension == Dimension.WEBSITE.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '1', 'name')[-1]
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get('ts')), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'website_id', id, *record_infos)
                    elif dimension == Dimension.SECTION.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '3',
                                               'pretty_name', 'website_id', 'website_name')[-1][-1]
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'section_id', id, *record_infos)
                    elif dimension == Dimension.PAGE.value:
                        record_infos = execute('FT.SEARCH', index_name, f'@id:{{{id}}}', 'RETURN', '5',
                                               'website_id', 'website_name', 'section_id',
                                               'section_pretty_name', 'article_id')[-1][-1]
                        execute('TS.ADD', timeseries_key_name, get_ts(parsed_key_name.get("ts")), pageviews,
                                'ON_DUPLICATE', 'LAST',
                                'LABELS', 'dimension', dimension, Dimension.METRIC.value, Metric.PAGEVIEWS.value,
                                'page_id', id, *record_infos)

            for id in records.get('id'):
                execute('XADD', output_stream_name, '*', 'dimension', dimension, 'id', id, 'ts', parsed_key_name.get('ts'))

            execute('EXPIRE', cms_merge.get('name'), key_expire_duration_sc)

    for cms_reinject in records.get('reinject'):
        for id in records.get('id'):
            execute('XADD', reinject_stream_name, '*', 'id', id, 'dimension', cms_reinject.get('dimension'), 'ts', cms_reinject.get('ts'))