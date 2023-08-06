from typing import List, Dict, Callable, Any
from datetime import datetime
from enum import Enum

from pararamio.utils import parse_datetime

__all__ = ('ActivityAction', 'Activity')


class ActivityAction(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'
    AWAY = 'away'
    READ = 'thread-read'
    POST = 'thread-post'
    CALL = 'calling'


class Activity:
    action: ActivityAction
    time: datetime

    def __init__(self, action: ActivityAction, time: datetime):
        self.action = action
        self.time = time

    def __str__(self):
        return str((self.time, self.action))

    @classmethod
    def _from_api_data(cls, data: Dict[str, str]) -> 'Activity':
        return cls(action=ActivityAction(data['action']), time=parse_datetime(data, 'datetime'))

    @classmethod
    def get_activity(cls, page_loader: Callable[..., Dict[str, Any]], start: datetime, end: datetime, actions: List[ActivityAction] = None) -> List['Activity']:
        results = []
        if not actions:
            actions = [None]
        for action in actions:
            page = 1
            is_last_page = False
            while not is_last_page:
                data = page_loader(action, page=page).get('data', [])
                if not data:
                    break
                for d in data:
                    act = Activity._from_api_data(d)
                    if act.time > end:
                        continue
                    if act.time < start:
                        is_last_page = True
                        break
                    results.append(act)
                page += 1
        return sorted(results, key=lambda x: x.time)
