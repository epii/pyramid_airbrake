import threading
import logging
import os
import sys
import time

from threadpool import NoResultsPending
from threadpool import ThreadPool
from threadpool import WorkRequest

from pyramid_airbrake.airbrake.submit import submit_payload
from pyramid_airbrake.handlers import BaseHandler

log = logging.getLogger(__name__)

def _exception_handler(request, exc_info):
    """
    Rudimentary exception handler, simply log and moves on.

    If there's no tuple, it means something went really wrong. Critically log
    and exit.

    """
    # this is done by django-hoptoad; I don't know why (or if) it is necessary
    if not isinstance(exc_info, tuple):
        log.critical(str(request))
        log.critical(str(exc_info))
        sys.exit(1)

    log.warn("Exception occured in request #{0}: {1}"
            .format(request.requestID, exc_info))


class ThreadedHandler(BaseHandler, threading.Thread):
    """Daemon thread that spawns a thread pool for sending Airbrake notices."""

    def __init__(self, settings):
        BaseHandler.__init__(self, settings)

        thread_name = 'Airbrake{0}-{1}'.format(self.__class__.__name__,
                                               os.getpid())
        threading.Thread.__init__(self, name=thread_name)

        self.n_threads = settings['threaded.threads']
        self.poll_interval = settings['threaded.poll_interval']

        self.daemon = True  # daemon thread -- important!
        self.pool = ThreadPool(self.n_threads)

        self.start()

    def report(self, payload):
        request = WorkRequest(
            self._submit,
            args=(payload,),
            exc_callback = _exception_handler
        )

        self.pool.putRequest(request)

    def run(self):
        """Poll the pool for results and process them."""

        while True:
            try:
                time.sleep(self.poll_interval)
                self.pool.poll()

            except NoResultsPending:
                pass
