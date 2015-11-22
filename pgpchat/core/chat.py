import json
import logging
import time
import sys

from pgpchat import Config

config = Config('nose' in sys.modules)

log = logging.getLogger(__name__)

class Client(object):
    def __init__(self):
        self.conn = config.redis_conn()
        pass

    def create_chat(self, sender, recipients, message, chat_id=None):
        chat_id = chat_id or str(self.conn.incr('ids:chat:'))

        recipients.append(sender)
        recipientsd = {r: 0 for r in recipients}
        with self.conn.pipeline(True) as pipeline:
            for rec in recipients:
                pipeline.zadd('seen:' + rec, chat_id, 0)
            pipeline.execute()

        return self.send_message(chat_id, sender, message)

    def send_message(self, chat_id, sender, message):
        #lock = acquire_lock(self.conn, 'chat:' + chat_id)
        #if not identifier:
        #    raise Exception("Unable to acquire lock")
        try:
            mid = self.conn.incr('ids:' + chat_id)
            ts = time.time()
            packed = json.dumps(dict(
                id=mid,
                ts=ts,
                sender=sender,
                message=message
            ))
            self.conn.zadd('msgs:' + chat_id, mid, packed)
        finally:
            pass
            #release_lock(self.conn, 'chat:' + chat_id, identifier)
        return chat_id

    def fetch_pending_messages(self, recipient):
        seen = self.conn.zrange('seen:' + recipient, 0, -1, withscores=True)

        with self.conn.pipeline(True) as pipeline:
            for chat_id, seen_id in seen:
                pipeline.zrangebyscore(
                    'msgs:' + chat_id.decode('utf-8'), seen_id + 1, 'inf')
                chat_info = list(zip(seen, pipeline.execute()))

            for i, ((chat_id, seen_id), messages) in enumerate(chat_info):
                if not messages:
                    continue

                chat_id = chat_id.decode('utf-8')
                messages[:] = map(lambda m: json.loads(m.decode('utf-8')), messages)
                seen_id = messages[-1]['id']
                self.conn.zadd('chat:' + chat_id, seen_id, recipient)
                min_id = self.conn.zrange(
                    'chat:' + chat_id, 0, 0, withscores=True)

                pipeline.zadd('seen:' + recipient, chat_id, seen_id)
                if min_id:
                    pipeline.zremrangebyscore(
                        'msgs:' + chat_id, 0, min_id[0][1])
                chat_info[i] = (chat_id, messages)
            pipeline.execute()
            return chat_info

    def join_chat(self, chat_id, user):
        message_id = int(self.conn.get('ids:' + chat_id))

        with self.conn.pipeline(True) as pipeline:
            pipeline.zadd('chat:' + chat_id, message_id, user)
            pipeline.execute()
            pipeline.zadd('seen:' + user, message_id, chat_id)
            pipeline.execute()

    def count_remaining_users(self, chat_id, pipeline=None):
        if pipeline:
            pipeline.zcard('chat:' + chat_id)
            return pipeline.execute()[-1]
        else:
            return self.conn.zard('chat:' + chat_id)

    def leave_chat(self, chat_id, user):
        with self.conn.pipeline(True) as pipeline:
            pipeline.zrem('chat:' + chat_id, user)
            pipeline.zrem('seen:' + user, chat_id)
            users_in_chat = count_remaining_users(chat_id, pipeline=pipeline)
            if not users_in_chat:
                pipeline.delete('msgs:' + chat_id)
                pipeline.delete('ids:' + chat_id)
                pipeline.execute()
            else:
                #delete old messages
                oldest = self.conn.zrange(
                    'chat:' + chat_id, 0, 0, withscores=True)
                self.conn.zremovebyscore('chat:' + chat_id, 0, oldest)
