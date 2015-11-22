import fakeredis
import redis

from pgpchat import app

class Config(object):

    def __init__(self, testing=False):
        self.testing = testing
        if testing:
            self.conn = fakeredis.FakeStrictRedis()
            self.conn.flushall()
        else:
            self.conn = redis.StrictRedis()

    def redis_conn(self):
        return self.conn

    def make_app(self):
        if not self.testing:
            app.debug = True
            app.app.run(port=5000)
