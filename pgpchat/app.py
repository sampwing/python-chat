from flask import Flask
from flask_restful import Api
from pgpchat.api import Chat

app = Flask(__name__)
api = Api(app)

# routes
api.add_resource(Chat, '/<string:chat_id>')
