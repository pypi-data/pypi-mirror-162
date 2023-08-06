from rgtracker.common import *

class Tracker:
    def __init__(self, GB):
        GB("KeysReader").foreach(lambda x: tracker_log(f'Message: {x}')).run(prefix='*')
