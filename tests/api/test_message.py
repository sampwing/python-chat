from tests import TestApp

class TestMessage(TestApp):

    def test_message(self):
        r = self.client.get('/')
        assert r.status_code == 200
