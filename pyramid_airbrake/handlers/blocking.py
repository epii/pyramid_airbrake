from pyramid_airbrake.handlers import BaseHandler

class BlockingHandler(BaseHandler):
    """Sends Airbrake notices immediately, blocking until completion."""

    def report(self, request):
        payload = self._payload(request)

        if payload:
            self._submit(payload)
