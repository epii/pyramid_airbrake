from pyramid_airbrake.handlers import BaseHandler

import logging

log = logging.getLogger(__name__)

class DummyHandler(BaseHandler):
    """Sends the XML report payloads directly to the python logging module."""

    def report(self, payload):
        log.error(payload)
