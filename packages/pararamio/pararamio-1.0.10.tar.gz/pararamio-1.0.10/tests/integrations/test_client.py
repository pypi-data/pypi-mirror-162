import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from http.cookiejar import MozillaCookieJar
from unittest.mock import MagicMock, patch
import logging

from pararamio.chat import Chat
from pararamio.client import Pararamio
from pararamio.deferred_post import DeferredPost
from pararamio.exceptions import PararamioException, PararamioValidationException
from pararamio.post import Post
from pararamio.user import User
from tests.integrations._base import BasePararamioTest


RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../resources')


class PararamioClientTest(BasePararamioTest):
    def setUp(self):
        super().setUp()
        if int(os.environ.get('DEBUG', 0)):
            logging.basicConfig(level=logging.DEBUG)
        self.recipient_email = os.environ.get('PARARAMIO_RECIPIENT_EMAIL', '')
        self.recipient_chat_id = os.environ.get('PARARAMIO_RECIPIENT_CHAT_ID', '')

    def test_001_login_without_cookie(self):
        client = Pararamio(**self.user1)
        self.assertIsNotNone(client.profile)

    def test_002_login_with_cookie(self):
        with tempfile.NamedTemporaryFile(suffix='.cookie') as tmp:
            MozillaCookieJar(tmp.name).save()
            client = Pararamio(**self.user1, cookie_path=tmp.name)
            self.assertIsNotNone(client.profile, 'Authentication failed')
            self.assertTrue(os.path.exists(tmp.name), 'Cookie path is not found')
            del client
            client = Pararamio(login='', password='', key='', cookie_path=tmp.name)
            self.assertIsNotNone(client.profile, 'Cookie authentication failed')

    def test_003_login_with_broken_cookie(self):
        with tempfile.NamedTemporaryFile(suffix='.cookie') as tmp:
            tmp.write('broken_cookie'.encode())
            client = Pararamio(**self.user1, cookie_path=tmp.name, ignore_broken_cookie=True)
            self.assertIsNotNone(client.profile, 'Authentication failed')
            self.assertTrue(os.path.exists(tmp.name), 'Cookie path is not found')

    def test_004_profile(self):
        self.assertEqual(self.client.profile.get('email'), self.user1['login'])

    def test_005_send_delete_file(self):
        d = {
            'size':     23050,
            'type':     'image/png',
            'filename': 'test.png'
        }
        post = None
        chat = Chat(self.client, self.recipient_chat_id)
        file = chat.upload_file(file_path=os.path.join(RESOURCES_PATH, 'test.png'))

        for _post in chat.posts(-5, -1):
            _post.load()
            if _post.file and _post.file.guid == file.guid:
                post = _post

        self.assertEqual(post.file.filename, d['filename'])
        self.assertIsNotNone(file)
        file.delete()
        self.assertDictEqual({
            'size':     file.size,
            'type':     post.file._data['mime_type'],
            'filename': file.filename
        },
            d)

    def test_006_list_own_threads(self):
        chats = self.client.list_chats()
        self.assertIsNotNone(chats)
        chat = next(chats)
        chat_ = Chat(self.client, chat.id)
        chat_.load()
        self.assertTrue(chat == chat_)

    def test_007_list_posts(self):
        chat = Chat(self.client, self.recipient_chat_id)
        self.assertTrue(chat.posts(-10, -1))
        self.assertTrue(chat.posts(0, 1))
        chat.load()
        exception = False
        try:
            chat.posts(1, 0)
        except PararamioValidationException:
            exception = True
        self.assertTrue(exception, 'posts load with invalid start end position')
        exception = False
        try:
            chat.posts(-1, -10)
        except PararamioValidationException:
            exception = True
        self.assertTrue(exception, 'posts load with invalid start end position')

    def test_008_search_user(self):
        self.assertIsNotNone(self.client.search_user('tamtambottester2@gmail.com'))
        self.assertIsNotNone(self.client.search_user('tamtambottester2'))
        self.assertIsNotNone(self.client.search_user('tamtam_bot_tester2'))

    def test_009_reply_to_post(self):
        chat = Chat(self.client, self.recipient_chat_id)
        post = chat.post('test')
        reply = post.reply('ReplyTest')
        self.assertEqual(post.post_no, reply.reply_no)

    def test_010_search_group(self):
        self.assertIsNotNone(self.client.search_group(''))

    def test_011_list_users(self):
        u = User(self.client, 58)
        u.load()

        self.assertTrue(u.unique_name)

    def test_012_chat_load(self, ):
        u = self.client.search_user('tamtambottester2@gmail.com')[0]
        chat = u.get_pm_thread()
        chat.load()
        pc = chat.posts_count
        u.post('text')
        chat.load()
        self.assertTrue(chat.posts_count == pc + 1)

    def test_013_read_status(self):
        u = self.client.search_user(self.recipient_email)[0]
        chat = u.get_pm_thread()
        chat.load()
        post = chat.post('test')
        chat.read_status(post.post_no + 1)
        self.assertTrue(chat.last_read_post_no == post.in_thread_no)

    def test_014_edit(self):
        u = self.client.search_user(self.recipient_email)[0]
        post = u.post('test')
        post.edit(text='TestTestStringString')
        chat = u.get_pm_thread()
        np = Post(chat, post.post_no)
        np.load()
        self.assertEqual('TestTestStringString', np.text)

    def test_015_send_and_delete_private_message(self):
        u = self.client.search_user(self.recipient_email)[0]
        post = u.post('test')
        self.assertIsNotNone(post)
        self.assertIsNotNone(post.delete())

    def test_016_send_and_delete_thread_message(self):
        chat = Chat(self.client, self.recipient_chat_id)
        post = chat.post('test')
        self.assertIsNotNone(post)
        self.assertIsNotNone(post.delete())

    def test_017_chat_methods(self):
        d = {'title': 'Test Create Chat', 'users': [self.client.profile['id']], 'pm': False, 'member_ids': [self.client.profile['id']]}
        chat = Chat.create(self.client2, **d)
        self.assertTrue(User(self.client, self.client.profile['id']) in chat)
        self.assertFalse(User(self.client, -1) in chat)
        self.assertTrue(Post(chat, post_no=1, ) in chat)
        self.assertFalse(Post(Chat(self.client, id=100), post_no=1) in chat)
        self.assertTrue(chat.id in [ch.id for ch in self.client.list_chats()], 'Thread is not created')
        chat.add_admins([self.client.profile['id']])
        chat.load()
        chat2 = Chat(self.client, chat.id).load()
        self.assertTrue(chat2.adm_flag, 'Admin is not set')
        time.sleep(5)
        chat.delete_admins([self.client.profile['id']])
        chat2.load()
        self.assertFalse(chat2.adm_flag, 'User is still admin')
        chat.delete()
        self.assertFalse(chat.id in [tr.id for tr in self.client.list_chats()], 'Thread is still exists')

    def test_018_deferred_posts(self):
        time_sending = datetime.now(tz=timezone.utc) + timedelta(days=1)
        text = f'{time_sending.timestamp()}: test deferred posts !'
        result = DeferredPost.create(self.client, self.recipient_chat_id, text, time_sending)
        self.assertTrue(result)
        posts = DeferredPost.get_deferred_posts(self.client)
        post = [p for p in posts if p.text == text]
        self.assertTrue(bool(post), 'Post is empty')
        self.assertTrue(post[0].text == text, 'text is not match')
        self.assertTrue(int(post[0].time_sending.timestamp()) == int(time_sending.timestamp()))
        post[0].delete()

    def test_019_posts_tree(self):
        chat = Chat(self.client, self.recipient_chat_id, posts_count=100)
        with patch.object(Post, 'rerere', return_value=[
            Post(chat, post_no=96, text='post no 96', reply_no=None),
            Post(chat, post_no=99, text='post no 99', reply_no=96),
            Post(chat, post_no=100, text='post no 100', reply_no=99, meta={})
        ]):
            with patch.object(chat, '_lazy_posts_loader', return_value=iter([
                Post(chat, post_no=96, text='post no 96', reply_no=None),
                Post(chat, post_no=97, text='post no 97', reply_no=None),
                Post(chat, post_no=98, text='post no 98', reply_no=96),
                Post(chat, post_no=99, text='post no 99', reply_no=96),
            ])):
                post = Post(chat, post_no=100, text='post no 100', reply_no=99, meta={})
                self.assertListEqual([96, 98, 99, 100], list(post.get_tree().keys()))
        many_fake_posts = [
            Post(chat, post_no=1, text='post no 1', reply_no=None),
            *[Post(chat, text=f'post no {i}', post_no=i, reply_no=i - 1) for i in range(2, 2000)],
            Post(chat, post_no=2000, text='post no 2000', reply_no=1999, meta={})
        ]

        def _load_posts_side_effect(start, end):
            return iter(many_fake_posts[start: end])

        with patch.object(Post, 'rerere', return_value=[many_fake_posts[0], *many_fake_posts[1000:]]):
            chat._load_posts = MagicMock(side_effect=_load_posts_side_effect)
            posts = list(many_fake_posts[-1].get_tree().keys())
            self.assertListEqual([many_fake_posts[0].post_no, *[p.post_no for p in many_fake_posts[1000:]]], posts)

        with patch.object(Post, 'rerere', return_value=[]):
            chat._load_posts = MagicMock(side_effect=lambda a, b: [])
            self.assertListEqual([2000], list(many_fake_posts[-1].get_tree().keys()))

    def test_020_send_and_delete_message_by_email(self):
        text = 'test by mail'
        try:
            self.client.post_private_message_by_user_email(self.recipient_email + '1111', text)
            self.assertTrue(False, 'the message cannot be sent to a non-existent email')
        except PararamioException:
            pass
        post = self.client.post_private_message_by_user_email(self.recipient_email, text)
        self.assertIsNotNone(post)
        self.assertTrue(post.text == text)
        self.assertIsNotNone(post.delete())

    def test_021_send_and_delete_message_by_id(self):
        text = 'test by mail'
        try:
            self.client.post_private_message_by_user_email(-1, text)
            self.assertTrue(False, 'the message cannot be sent to a non-existent id')
        except PararamioException:
            pass
        post = self.client.post_private_message_by_user_id(self.client2.profile['id'], text)
        self.assertIsNotNone(post)
        self.assertTrue(post.text == text)
        self.assertIsNotNone(post.delete())

    @classmethod
    def tearDownClass(cls):
        if os.path.exists('test.cookie'):
            os.remove('test.cookie')
        if os.path.exists('test.cookie2'):
            os.remove('test.cookie2')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PararamioClientTest)


if __name__ == "__main__":
    unittest.main()
