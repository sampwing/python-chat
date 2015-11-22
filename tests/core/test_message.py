from pgpchat.core import Client
from nose.tools import assert_in, assert_not_equal

class TestChat(object):
    def setup(self):
        self.client = Client()
        self.user1 = 'user1'
        self.user2 = 'user2'
        self.message = 'test message'

    def test_create_chat(self):
        chat_id = '1'
        given_chat_id = self.client.create_chat(sender=self.user1, recipients=[self.user2], message=self.message, chat_id=chat_id)
        assert chat_id == given_chat_id

    def test_recieve_message(self):
        chat_id = self.client.create_chat(sender=self.user1, recipients=[self.user2], message=self.message)
        self.client.join_chat(chat_id=chat_id, user=self.user2)

        self.client.send_message(chat_id, sender=self.user1, message=self.message)
        self.client.send_message(chat_id, sender=self.user1, message=self.message)
        messages = self.client.fetch_pending_messages(self.user2)
        chat_messages = list(filter(lambda i: i[0] == chat_id, messages))
        assert_in(self.message, messages)


