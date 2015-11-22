import json
import logging

log = logging.getLogger(__name__)

class Message(object):
    def __init__(self, sender, timestamp, id, message, *args, **kwargs):
        self.fields = ['sender', 'timestamp', 'id', 'message']
        self.sender = sender
        self.timestamp = timestamp
        self.id = id
        self.message = message

    @classmethod
    def from_json(cls, json_):
        try:
            if hasattr(json_, 'decode'):
                blob = json.loads(json_.decode('utf-8'))
            else:
                blob = json.loads(json_)
            return Message(**blob)
        except Exception as e:
            log.error(e)
            raise e

    def to_json(self):
        try:
            dict_ = {field: getattr(self, field) for field in self.fields}
            return json.dumps(dict_)
        except Exception as e:
            log.error(e)
            raise e
