from pyramid_airbrake.handlers import BaseHandler

class BlockingHandler(BaseHandler):
    """Sends Airbrake notices immediately, blocking until completion."""

    def report(self, payload):
        self._submit(payload)
