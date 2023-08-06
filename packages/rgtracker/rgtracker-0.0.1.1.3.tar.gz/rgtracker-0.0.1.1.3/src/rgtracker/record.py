from rgtracker.common import *
from rgtracker.tracker import *
from rgtracker.common import *
from rgtracker.website import *
from rgtracker.section import *
from rgtracker.page import *
from rgtracker.device import *
from dataclasses import dataclass, field


@dataclass
class Record:
    """
    Represent any records read with Redis Gears

    Examples
    --------
    Record.key = TYPE:optional(NAME):optional(DIMENSION):optional(RECORD_ID):optional(DATETIME):optional(METRIC)
    """
    redis_event: str
    redis_key: str
    redis_type: str
    redis_value: dict
    type: field(init=False) = None
    name: field(init=False) = None
    dimension: field(init=False) = None
    record_id: field(init=False) = None
    ts: field(init=False) = None
    metric_id: field(init=False) = None

    def __post_init__(self):
        key_split = self.redis_key.split(':')
        self.type = self.check_none(key_split[RedisNC.TYPE])
        self.name = self.check_none(key_split[RedisNC.NAME])
        self.dimension = self.check_none(key_split[RedisNC.DIMENSION])
        self.record_id = self.check_none(key_split[RedisNC.RECORD_ID])
        self.ts = self.check_none(key_split[RedisNC.TS])
        self.metric = self.check_none(key_split[RedisNC.METRIC])

    @staticmethod
    def check_none(check_value):
        if check_value == '':
            return None
        else:
            return check_value

    def serialize_record(self):
        # Todo: use from_dict
        if self.type == Type.STREAM.value:
            # Todo: check schema version with metadata field and create 'Stream' object
            if self.name == 'TRACKER':
                return Tracker(
                    uui=self.redis_value.get('uui'),
                    url=self.redis_value.get('url'),
                    ts=self.redis_value.get('dt'),
                    metadata=self.redis_value.get('metadata'),
                )
            elif self.name.startswith('BLOOM-ROTATE'):
                if self.redis_value.get('dimension') == Dimension.WEBSITE.value:
                    # log(f'Record - {self}')
                    # log(f'Record - {self.record_id}')
                    # log(f"Record - {self.redis_value.get('key').split(':')[RedisNC.RECORD_ID]}")
                    x = Website(
                        id=self.redis_value.get('key').split(':')[RedisNC.RECORD_ID],
                        last_visited=self.redis_value.get('key').split(':')[RedisNC.TS]
                    )
                    return x
                elif self.redis_value.get('dimension') == Dimension.SECTION.value:
                    return Section(
                        id=self.redis_value.get('key').split(':')[RedisNC.RECORD_ID],
                        last_visited=self.redis_value.get('key').split(':')[RedisNC.TS]
                    )
                elif self.redis_value.get('dimension') == Dimension.PAGE.value:
                    return Page(
                        id=self.redis_value.get('key').split(':')[RedisNC.RECORD_ID],
                        last_visited=self.redis_value.get('key').split(':')[RedisNC.TS]
                    )
                else:
                    raise ValueError
            else:
                raise ValueError
        else:
            if self.dimension == Dimension.WEBSITE.value:
                # return from_dict(data_class=Website, data={
                #     'id': self.record_id,
                #     'name': None  # self.get_dimension_value()
                # })
                raise NotImplementedError
            elif self.dimension == Dimension.SECTION.value:
                # return from_dict(data_class=Section, data={
                #     'id': self.record_id,
                #     'name': None  # self.get_dimension_value()
                # })
                raise NotImplementedError
            elif self.dimension == Dimension.PAGE.value:
                # return from_dict(data_class=Section, data={
                #     'id': self.record_id,
                #     'name': None  # self.get_dimension_value()
                # })
                raise NotImplementedError
            elif self.dimension == Dimension.DEVICE.value:
                # return from_dict(data_class=Section, data={
                #     'id': self.record_id,
                #     'name': None  # self.get_dimension_value()
                # })
                raise NotImplementedError
            else:
                raise ValueError
