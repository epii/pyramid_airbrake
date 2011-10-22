from pyramid_airbrake.airbrake.apiv21 import derive_report

import logging

log = logging.getLogger(__name__)

class DummyHandler(object):
    def __init__(self, settings):
        self.settings = settings

    def report(self, request):
        payload = derive_report(self.settings, request)
        log.error(payload)


def get_handler(settings):
    return DummyHandler(settings)
