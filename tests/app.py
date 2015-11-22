from pgpchat.app import app

class TestApp(object):

    def setup(self):
        self.client = app.test_client()
        self.client.testing = True
