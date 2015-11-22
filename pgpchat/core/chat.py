import logging
import time
import sys

from pgpchat.config import Config
from pgpchat.core.message import Message

config = Config('nose' in sys.modules)

log = logging.getLogger(__name__)

CHAT_ID = 'ids:chat:'
CHAT = 'chat:'
SEEN = 'seen:'
MESSAGE_ID = 'ids:'
MESSAGES = 'msgs:'

class Client(object):
    def __init__(self):
        self.conn = config.redis_conn()

    def create_chat(self, sender, recipients, message, chat_id=None):
        chat_id = chat_id or str(self.conn.incr(CHAT_ID))

        recipients.append(sender)
        recipientsd = {r: 0 for r in recipients}
        with self.conn.pipeline(True) as pipeline:
            for rec in recipients:
                pipeline.zadd(SEEN + rec, chat_id, 0)
            pipeline.execute()

        return self.send_message(chat_id, sender, message)

    def send_message(self, chat_id, sender, message):
        #lock = acquire_lock(self.conn, CHAT + chat_id)
        #if not identifier:
        #    raise Exception("Unable to acquire lock")
        try:
            mid = self.conn.incr(MESSAGE_ID + chat_id)
            timestamp = time.time()
            msg = Message(id=mid, 
                          sender=sender, 
                          timestamp=timestamp, 
                          message=message)
            self.conn.zadd(MESSAGES + chat_id, mid, msg.to_json())
        except Exception as e:
            log.error(e)
        finally:
            pass
            #release_lock(self.conn, CHAT + chat_id, identifier)
        return chat_id

    def fetch_pending_messages(self, recipient):
        seen = self.conn.zrange(SEEN + recipient, 0, -1, withscores=True)

        with self.conn.pipeline(True) as pipeline:
            for chat_id, seen_id in seen:
                pipeline.zrangebyscore(MESSAGES + chat_id.decode('utf-8'), 
                                       seen_id + 1, 'inf')
                chat_info = list(zip(seen, pipeline.execute()))

            for i, ((chat_id, seen_id), messages) in enumerate(chat_info):
                if not messages:
                    continue

                chat_id = chat_id.decode('utf-8')
                messages = [Message.from_json(m) for m in messages] 
                last_message = messages[-1]
                seen_id = last_message.id

                self.conn.zadd(CHAT + chat_id, seen_id, recipient)
                min_id = self.conn.zrange(
                    CHAT + chat_id, 0, 0, withscores=True)

                pipeline.zadd(SEEN + recipient, chat_id, seen_id)
                if min_id:
                    pipeline.zremrangebyscore(
                        MESSAGES + chat_id, 0, min_id[0][1])
                chat_info[i] = (chat_id, messages)
            pipeline.execute()
            return chat_info

    def join_chat(self, chat_id, user):
        message_id = int(self.conn.get(MESSAGE_ID + chat_id))

        with self.conn.pipeline(True) as pipeline:
            pipeline.zadd(CHAT + chat_id, message_id, user)
            pipeline.zadd(SEEN + user, message_id, chat_id)
            pipeline.execute()

    def count_remaining_users(self, chat_id, pipeline=None):
        if pipeline:
            pipeline.zcard(CHAT + chat_id)
            return pipeline.execute()[-1]
        else:
            return self.conn.zard(CHAT + chat_id)

    def leave_chat(self, chat_id, user):
        with self.conn.pipeline(True) as pipeline:
            pipeline.zrem(CHAT + chat_id, user)
            pipeline.zrem(SEEN + user, chat_id)
            users_in_chat = count_remaining_users(chat_id, pipeline=pipeline)
            if not users_in_chat:
                pipeline.delete(MESSAGES + chat_id)
                pipeline.delete(MESSAGE_ID + chat_id)
                pipeline.execute()
            else:
                #delete old messages
                oldest = self.conn.zrange(CHAT + chat_id, 0, 0, withscores=True)
                self.conn.zremovebyscore(CHAT + chat_id, 0, oldest)
