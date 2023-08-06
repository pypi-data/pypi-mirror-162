from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING

from pararamio._types import PostMetaT
from pararamio.exceptions import PararamioRequestException
from pararamio.file import File
from pararamio.utils.helpers import encode_digit, parse_datetime, rand_id


if TYPE_CHECKING:
    from pararamio.chat import Chat
    from pararamio.client import Pararamio

__all__ = ('Post',)
ATTR_FORMATTERS = {
    'post_no':      lambda data, key: int(data[key]),
    'time_edited':  parse_datetime,
    'time_created': parse_datetime,
}


class Post:
    __slots__ = ('_data', '_chat', 'post_no', 'load_on_key_error')
    _data: Dict[str, Any]
    _chat: 'Chat'
    post_no: int
    text: str
    text_parsed: Optional[List[Dict[str, Any]]]
    user_id: int
    event: Optional[Dict[str, Any]]
    time_created: datetime
    time_edited: Optional[datetime]
    reply_no: Optional[int]
    meta: 'PostMetaT'
    uuid: Optional[str]
    load_on_key_error: bool

    def __init__(self, chat: 'Chat', post_no: int = None, load_on_key_error: bool = True, **kwargs):
        self._chat = chat
        if post_no is None:
            post_no = kwargs['in_thread_no']
        self.post_no = post_no
        self._data = {**kwargs, 'post_no': post_no}
        self.load_on_key_error = load_on_key_error

    def __getattr__(self, name):
        fmt_fnc = ATTR_FORMATTERS.get(name, None)
        if fmt_fnc:
            return fmt_fnc(self._data, name)
        try:
            return self._data[name]
        except KeyError:
            if self.load_on_key_error:
                self.load()
                return self._data[name]
            raise

    def __repr__(self):
        return f'<Post(client={hex(id(self.client))}, chat_id={self.chat_id}, post_no={self.post_no}) {hex(id(self))}>'

    def __str__(self):
        text = self._data.get('text', None)
        if text is None:
            self.load()
            text = self._data['text']
        return text

    def __eq__(self, other):
        if not isinstance(other, Post):
            return id(other) == id(self)
        return self._chat == other._chat and self.post_no == other.post_no

    def _compare_validations(self, other):
        if not isinstance(other, Post):
            raise ValueError('can not compare post and {}'.format(other.__class__.__name__))
        if self._chat != other._chat:
            raise ValueError('can not compare posts from different chats')

    def __ge__(self, other: 'Post'):
        self._compare_validations(other)
        # noinspection PyUnresolvedReferences
        return self.post_no >= other.post_no  # type: ignore[operator]

    def __gt__(self, other: 'Post'):
        self._compare_validations(other)
        # noinspection PyUnresolvedReferences
        return self.post_no > other.post_no  # type: ignore[operator]

    def __lt__(self, other: 'Post'):
        self._compare_validations(other)
        # noinspection PyUnresolvedReferences
        return self.post_no < other.post_no  # type: ignore[operator]

    def __le__(self, other: 'Post'):
        self._compare_validations(other)
        # noinspection PyUnresolvedReferences
        return self.post_no <= other.post_no  # type: ignore[operator]

    @property
    def chat_id(self) -> int:
        return self._chat.id

    @property
    def in_thread_no(self) -> int:
        return self.post_no

    @property
    def file(self):
        return self.files

    @property
    def files(self):
        _file = self._data.get('meta', {}).get('file', None)
        if not _file:
            return
        return File(self._chat._client, **_file)

    @property
    def is_reply(self) -> bool:
        return self._data.get('reply_no', None) is not None

    @property
    def is_deleted(self) -> bool:
        return bool(self._data.get('text', None))

    @property
    def chat(self) -> 'Chat':
        return self._chat

    @property
    def client(self) -> 'Pararamio':
        return self._chat._client

    def sync(self):
        # TODO: Implement sync
        raise NotImplementedError()

    def load(self) -> 'Post':
        url = f'/msg/post?ids={encode_digit(self.chat.id)}-{encode_digit(self.post_no)}'  # type: ignore
        res = self.client.api_get(url).get('posts', [])
        if len(res) != 1:
            raise PararamioRequestException(f'failed to load data for post_no {self.post_no} in chat {self._chat.id}')
        self._data = res[0]
        return self

    @property
    def replies(self):
        url = f'/msg/post/{self._chat.id}/{self.post_no}/replies'
        return self.client.api_get(url)

    def reply(self, text: str, quote: Optional[str] = None) -> 'Post':
        _url = f'/amsg/post/{self._chat.id}'
        res = self.client.api_post(_url, {
            'uuid':     rand_id(),
            'text':     text,
            'quote':    quote,
            'reply_no': self.post_no
        })
        return Post(self._chat, res['post_no'], load_on_key_error=self.load_on_key_error).load()

    def rerere(self) -> Iterable['Post']:
        url = f'/msg/post/{self._chat.id}/{self.post_no}/rerere'
        res = self.client.api_get(url)

        def make_post_from_re(post_no):
            return Post(self._chat, post_no, load_on_key_error=self.load_on_key_error).load()

        return map(make_post_from_re, res['data'])

    def get_tree(self, load_limit: int = 1000) -> 'OrderedDict[int, Post]':
        posts = {self.post_no: self}
        for post in self.rerere():
            posts[post.post_no] = post
        first = posts[min(posts.keys())]
        tree = OrderedDict(sorted(posts.items()))  # type: ignore
        load_start = first.post_no + 1
        if self.post_no - first.post_no > load_limit:
            load_start = self.post_no - load_limit
        for post in self.chat._lazy_posts_loader(*sorted([load_start, self.post_no - 1])):
            posts[post.post_no] = post

        for no, post in sorted(posts.items()):
            if post.reply_no is None or post.reply_no not in tree:
                continue
            tree[post.post_no] = post
        return OrderedDict(sorted(tree.items()))  # type: ignore

    def get_reply_to_post(self) -> Optional['Post']:
        reply_no = self.reply_no
        if reply_no is not None:
            return Post(self._chat, reply_no, load_on_key_error=self.load_on_key_error).load()
        return None

    def who_read(self) -> List[int]:
        url = f'/activity/who-read?thread_id={self._chat.id}&post_no={self.post_no}'
        return self.client.api_get(url).get('users', [])

    def edit(self, text: str, quote: Optional[str] = None, reply_no: int = None) -> bool:
        """
        :param quote: str, used with reply_no, default None
        :param reply_no: int reply to, default None
        :param text: str Text to change
        :return: Post
        """
        url = f'/amsg/post/{self._chat.id}/{self.post_no}'

        res = self.client.api_put(url, {
            'uuid':     self._data.get('uuid', rand_id()),
            'text':     text,
            'quote':    quote,
            'reply_no': reply_no
        })
        if res.get('ver'):
            self.load()
            return True
        return False

    def delete(self) -> bool:
        url = f'/amsg/post/{self._chat.id}/{self.post_no}'
        res = self.client.api_delete(url)
        if res.get('ver'):
            self.load()
            return True
        return False

    @classmethod
    def create(cls, chat: 'Chat', text: str, reply_no: Optional[int] = None, quote: Optional[str] = None) -> 'Post':
        url = f'/amsg/post/{chat.id}'
        res = chat._client.api_post(url, {
            'uuid':  rand_id(), 'text': text,
            'quote': quote, 'reply_no': reply_no
        })

        if not res:
            raise PararamioRequestException('Failed to create post')

        return cls(chat, post_no=res['post_no']).load()
