from rgtracker.record import *
from rgtracker.tracker import *
from rgtracker.common import *
from rgtracker.website import *
from rgtracker.section import *
from rgtracker.page import *
from rgtracker.device import *


def transform(record):
    serialized_object = Record(
        redis_event=record.get('event'),
        redis_key=record.get('key'),
        redis_type=record.get('type'),
        redis_value=record.get('value')
    ).serialize_record()

    if type(serialized_object) is Tracker:
        return serialized_object.serialize_tracker()
    else:
        raise Exception(f'Record is not a Tracker object')


def load(tracker):
    website: Website = tracker.get('website')
    section = tracker.get('section')
    page = tracker.get('page')
    device = tracker.get('device')

    load_website(website, section, page, device)

    return tracker


# Create Index

GB("StreamReader"). \
    map(transform). \
    foreach(load). \
    register(
    prefix='ST:TRACKER::::',
    convertToStr=True,
    collect=True,
    onFailedPolicy='abort',
    onFailedRetryInterval=1,
    batch=1,
    duration=0,
    trimStream=False)

# run('ST:TRACKER::::', trimStream=False)
# register(
# prefix='ST:TRACKER::::',
# convertToStr=True,
# collect=True,
# onFailedPolicy='abort',
# onFailedRetryInterval=1,
# batch=1,
# duration=0,
# trimStream=False)
