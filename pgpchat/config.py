import fakeredis
import redis

from pgpchat import app

class Config(object):

    def __init__(self, testing=False):
        self.testing = testing

    def redis_conn(self):
        if self.testing:
            conn = fakeredis.FakeStrictRedis()
            conn.flushall()
            return conn
        else:
            return redis.StrictRedis()

    def make_app(self):
        if not self.testing:
            app.debug = True
            app.run(port=5000)
