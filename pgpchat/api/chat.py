import logging
from collections import OrderedDict

from flask import request
from flask_restful import fields, marshal_with, Resource, reqparse

from pgpchat.core import Client

ACTION = 'action'
JOIN = 'join'
LEAVE = 'leave'
MESSAGE = 'message'

parser = reqparse.RequestParser()
parser.add_argument(ACTION, type=str, help='Action to take')

client = Client()

log = logging.getLogger(__name__)

chat_resource_fields = {
    'chat_id': fields.String
}
class ChatDao(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id

user = 'fakeuser'
class Chat(Resource):
    def get(self):
        # list
        return {'available_rooms': []}

    #@marshal_with(chat_resource_fields)
    def post(self):
        # create chat
        try:
            message = request.form[MESSAGE]
            chat_id = client.create_chat(sender=user, 
                                         recipients=[user], 
                                         message=message)
            return ChatDao(chat_id=chat_id)
        except Exception as e:
            log.error(e)
            return {'error': 'internal: {}'.format(e)}, 500

    def put(self, chat_id):
        # handle joining and leaving a chat
        args = parser.parse_args()
        action = args.get(ACTION)
        if not action:
            return {'error': 'no action provided'}, 400

        if action == JOIN:
            try:
                client.join_chat(chat_id, user)
            except Exception as e:
                log.error(e)
                return {'error': 'internal'}, 500
        elif action == LEAVE:
            try:
                client.leave_chat(chat_id, user)
            except Exception as e:
                log.error(e)
                return {'error': 'internal'}, 500
        else:
            return {'error': 'action: "{}" is invalid'}, 400



