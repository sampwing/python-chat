from flask_restful import Resource
class Chat(Resource):
    def get(self):
        return {'available_rooms': []}
