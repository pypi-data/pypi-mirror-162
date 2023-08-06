from rgtracker.common import *
from redis import Redis
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


def create_website_index(redis_conn):
    try:
        index_name = create_key_name(
            type=Type.INDEX.value, name='',
            dimension=Dimension.WEBSITE.value, record_id='',
            ts='', metric='')
        schema = (
            TagField('$.id', as_name='id'),
            TextField('$.name', as_name='name'),
            NumericField("$.last_visited", as_name='last_visited', sortable=True),
            TagField(name='$.sections[*].id', as_name='section_id'),
            TagField('$.sections[*].pretty_name', as_name='section_pretty_name', separator='/'),
            # NumericField('$.sections[*].last_visited', as_name='section_last_visited', sortable=True),
            TagField(name='$.pages[*].id', as_name='page_id'),
            # TagField('$.pages[0:].url', as_name='page_url'),
            # TagField('$.pages[*].article_id', as_name='page_article_id'),
            # NumericField('$.pages[0:].last_visited', as_name='page_last_visited', sortable=True),
        )
        definition = IndexDefinition(prefix=['J::W:'], index_type=IndexType.JSON)
        redis_conn.ft(index_name).create_index(schema, definition=definition)
    except Exception as e:
        print(f'Error when creating Redis index: {e}')
        pass


def create_section_index(redis_conn):
    try:
        index_name = create_key_name(
            type=Type.INDEX.value, name='',
            dimension=Dimension.SECTION.value, record_id='',
            ts='', metric='')
        schema = (
            TagField('$.id', as_name='id'),
            TagField('$.pretty_name', as_name='pretty_name', separator='/'),
            TagField('$.level_0', as_name='level_0'),
            TagField('$.level_1', as_name='level_1'),
            TagField('$.level_2', as_name='level_2'),
            TagField('$.level_3', as_name='level_3'),
            TagField('$.level_4', as_name='level_4'),
            NumericField("$.last_visited", as_name='last_visited', sortable=True),
            TagField(name='$.website.id', as_name='website_id'),
            TagField('$.website.name', as_name='website_name'),
        )
        definition = IndexDefinition(prefix=['J::S:'], index_type=IndexType.JSON)
        redis_conn.ft(index_name).create_index(schema, definition=definition)
    except Exception as e:
        print(f'Error when creating Redis index: {e}')
        pass


def create_page_index(redis_conn):
    try:
        index_name = create_key_name(
            type=Type.INDEX.value, name='',
            dimension=Dimension.PAGE.value, record_id='',
            ts='', metric='')
        schema = (
            TagField('$.id', as_name='id'),
            TextField('$.url', as_name='url'),
            # TagField('$.article_id', as_name='article_id'), # Tag field doesn't accept int field -> str(article_id)
            NumericField("$.last_visited", as_name='last_visited', sortable=True),
            TagField(name='$.website.id', as_name='website_id'),
            TagField('$.website.name', as_name='website_name'),
            TagField(name='$.section.id', as_name='section_id'),
            TagField('$.section.pretty_name', as_name='section_pretty_name', separator='/'),
            TagField('$.section.levels.level_0', as_name='section_level_0'),
            TagField('$.section.levels.level_1', as_name='section_level_1'),
            TagField('$.section.levels.level_2', as_name='section_level_2'),
            TagField('$.section.levels.level_3', as_name='section_level_3'),
            TagField('$.section.levels.level_4', as_name='section_level_4'),
        )
        definition = IndexDefinition(prefix=['J::P:'], index_type=IndexType.JSON)
        redis_conn.ft(index_name).create_index(schema, definition=definition)
    except Exception as e:
        print(f'Error when creating Redis index: {e}')
        pass

redis_conn = Redis(host="localhost", port=6379)

create_website_index(redis_conn)
create_section_index(redis_conn)
create_page_index(redis_conn)
