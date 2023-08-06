from rgtracker.common import *
from rgtracker.website import *
from rgtracker.section import *
from rgtracker.page import *
from rgtracker.device import *
import hashlib
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse


@dataclass
class Tracker:
    """Represent Main object in Tracker project. Come from ST:TRACKER:::: Stream"""
    uui: str
    url: str
    ts: str
    metadata: dict
    website: field(init=False) = None
    section: field(init=False) = None
    page: field(init=False) = None

    def __post_init__(self):
        x = self.harmonize_url(self.url)
        self.website = x.get('website')
        self.section = x.get('section')
        self.page = x.get('page')

    @staticmethod
    def generate_id(value):
        return hashlib.sha1(str(value).encode('utf-8')).hexdigest()

    def harmonize_url(self, url):
        o = urlparse(url)

        website = o.hostname
        if website == 'www.rtl.lu':
            website = 'rtl'
        elif website == '5minutes.rtl.lu':
            website = '5minutes'
        elif website == 'today.rtl.lu':
            website = 'today'
        elif website == 'www.eldo.lu':
            website = 'eldo'
        else:
            website = None

        level_values = list(PurePosixPath(unquote(o.path)).parts)
        level_values.append(level_values.pop(-1).split('.')[0])

        level_ids = ["level_{}".format(i) for i in range(len(level_values))]
        levels = dict(zip(level_ids, level_values))

        section = None
        if len(level_values) > 2:
            section = f"{level_values[1]}/{level_values[2]}"
        else:
            section = f"{level_values[1]}"

        clean_url = o.scheme + "://" + o.netloc + o.path
        article_id = int(level_values[-1]) if level_values[-1].isdigit() else None

        return {
            'website': {
                'id': self.generate_id(website),
                'name': website,
                'last_visited': self.ts
            },
            'section': {
                'id': self.generate_id(section),
                'pretty_name': section,
                'levels': levels,
                'last_visited': self.ts
            },
            'page': {
                'id': self.generate_id(clean_url),
                'url': clean_url,
                'last_visited': self.ts,
                'article_id': article_id,
            }
        }

    def serialize_tracker(self):
        return {
            'website': Website(
                id=self.website.get('id'),
                name=self.website.get('name'),
                last_visited=self.website.get('last_visited')
            ),
            'section': Section(
                id=self.section.get('id'),
                pretty_name=self.section.get('pretty_name'),
                levels=dict(self.section.get('levels')),
                last_visited=self.section.get('last_visited')
            ),
            'page': Page(
                id=self.page.get('id'),
                url=self.page.get('url'),
                article_id=self.page.get('article_id'),
                last_visited=self.page.get('last_visited')
            ),
            'device': Device(id=self.uui)
        }
