import unittest
from pyramid import testing

class Test_airbrake_tween_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={'airbrake.api_key': '01234'})
        self.registry = self.config.registry

    def _callFUT(self):
        from pyramid_airbrake import airbrake_tween_factory
        return airbrake_tween_factory(None, self.registry)

    def test_no_recipients(self):
        handler = self._callFUT()
        assert handler.__name__ == 'airbrake_tween'


class DummyConfig(object):
    def __init__(self):
        self.tweens = []
        self.registry = self
        self.settings = {}

    def add_tween(self, factory, under=None, over=None):
        self.tweens.append((factory, under, over))
