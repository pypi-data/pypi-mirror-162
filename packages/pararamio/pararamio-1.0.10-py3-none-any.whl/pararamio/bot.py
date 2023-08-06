from typing import Any, Callable, Dict, Iterable, List, Optional, Union, TYPE_CHECKING

from pararamio.exceptions import PararamioRequestException
from pararamio.utils import bot_request, join_ids, lazy_loader
from pararamio.activity import Activity, ActivityAction

if TYPE_CHECKING:
    from datetime import datetime


__all__ = ('PararamioBot',)


def _load_chats(cls, ids: List[int]) -> List[Dict[str, Any]]:
    url = f'/core/chat?ids={join_ids(ids)}'
    res = cls.request(url)
    if res and 'chats' in res:
        return [data for data in cls.request(url).get('chats', [])]
    raise PararamioRequestException('failed to load data for chats ids: {}'.format(','.join(map(str, ids))))


def _one_or_value_error(fn: Callable, msg: str, *args) -> Any:
    try:
        return fn()[0]
    except IndexError:
        pass
    raise ValueError(msg.format(*args))


class PararamioBot:
    key: str

    def __init__(self, key: str):
        if len(key) > 50:
            key = key[20:]
        self.key = key

    def request(self, url: str, method: str = 'GET', data: Optional[dict] = None, headers: dict = None) -> Dict:
        return bot_request(url, self.key, method=method, data=data, headers=headers)

    def profile(self):
        """

        :return: {
            "id":12981,
            "active":true,
            "deleted":false,
            "email":null,
            "find_strict":false,
            "has_password":false,
            "info":null,
            "info_parsed":[],
            "info_chat":43611,
            "is_bot":true,
            "is_google":false,
            "name":"ChatHelpBot",
            "name_trans":"",
            "unique_name":"helpbot",
            "organizations":[293,1],
            "phoneconfirmed":false,
            "phonenumber":null,
            "time_created":"2019-08-14T05:25:04.088435Z",
            "time_updated":"2019-09-04T04:37:26.065742Z",
            "two_step_enabled":false
        }
        """
        url = '/user/me'
        return self.request(url)

    def post_message(self, chat_id: int, text: str, reply_no: Optional[int] = None) -> Dict[str, Union[str, int]]:
        url = '/bot/message'
        return self.request(url, method='POST', data={'chat_id': chat_id, 'text': text, 'reply_no': reply_no})

    def post_private_message_by_user_id(self, user_id: int, text: str) -> Dict[str, Union[str, int]]:
        url = '/msg/post/private'
        return self.request(url, method='POST', data={'text': text, 'user_id': user_id})

    def post_private_message_by_user_email(self, email: str, text: str) -> Dict[str, Union[str, int]]:
        url = '/msg/post/private'
        return self.request(url, method='POST', data={'text': text, 'user_email': email})

    def post_private_message_by_user_unique_name(self, unique_name: str, text: str) -> Dict[str, Union[str, int]]:
        url = '/msg/post/private'
        return self.request(url, method='POST', data={'text': text, 'user_unique_name': unique_name})

    def get_tasks(self) -> Dict[str, Any]:
        url = '/msg/task'
        return self.request(url)

    def set_task_status(self, chat_id: int, post_no: int, state: str) -> Dict:
        if str.lower(state) not in ('open', 'done', 'close'):
            raise ValueError(f'unknown state {state}')
        url = f'/msg/task/{chat_id}/{post_no}'
        data = {'state': state}
        return self.request(url, method='POST', data=data)

    def get_chat(self, chat_id) -> Dict[str, Any]:
        url = f'/core/chat?ids={chat_id}'
        return _one_or_value_error(lambda: self.request(url).get('chats', []), 'chat with id {0} is not found', chat_id)

    def get_chats(self) -> Iterable[dict]:
        url = '/core/chat/sync'
        chats_per_load = 50
        ids = self.request(url).get('chats', [])
        return lazy_loader(self, ids, _load_chats, per_load=chats_per_load)

    def get_users(self, users_ids: List[int]) -> Dict[str, Any]:
        url = f'/core/user?ids={join_ids(users_ids)}'
        return self.request(url).get('users', [])

    def get_user_by_id(self, user_id: int):
        return _one_or_value_error(lambda: self.get_users([user_id]), 'user with id {0} is not found', user_id)

    def _user_activity_page_loader(self, user_id: int) -> Callable[..., Dict[str, Any]]:
        def loader(action: ActivityAction = None, page: int = 1) -> Dict[str, Any]:
            action_ = action.value if action else ''
            url = f'/activity?user_id={user_id}&action={action_}&page={page}'
            return self.request(url)

        return loader

    def get_user_activity(self, user_id: int, start: 'datetime', end: 'datetime', actions: List[ActivityAction] = None) -> List[Activity]:
        """get user activity by user_id

        :param user_id: user id
        :param start: start time
        :param end: end time
        :param actions: list of action types (all actions if None)
        :returns: activity list
        """
        return Activity.get_activity(self._user_activity_page_loader(user_id), start, end, actions)
