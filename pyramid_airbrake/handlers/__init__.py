from pyramid_airbrake.airbrake.submit import create_http_pool
from pyramid_airbrake.airbrake.submit import submit_payload

import logging

log = logging.getLogger(__name__)

def get_handler(settings):
    """
    Handler factory.

    `settings` should be the result of running
    `pyramid_airbrake.settings.parse_pyramid_settings` over a Pyramid
    deployment settings object.

    The handler may be chosen with the `airbrake.handler` setting.  The
    following options are valid:

    `dummy`
        Sends XML reports to the Python standard logging facility.

    `blocking`
        Sends reports to Airbrake, blocking until it is sent or the submission
        times out.

    `threaded`
        Sends reports to Airbrake using a thread pool.

    Defaults to `dummy`.

    Currently, most of the logic for this is handled in
    `pyramid_airbrake.settings.parse_pyramid_settings`.

    """
    return settings['handler'](settings)


class BaseHandler(object):
    def __init__(self, settings):
        # CPython dicts are thread-safe for read-only ops, but thread safety is
        # not guranteed by the Python spec; so set these here because Handler
        # classes may require thread safety
        self.notification_url = settings['notification_url']
        self.http_pool = create_http_pool(settings)

    def _submit(self, payload):
        """Safely submits the XML `payload` to Airbrake; returns True on
        success and False on error."""

        try:
            result = submit_payload(payload, self.http_pool,
                                    self.notification_url)
        except BaseException as exc:
            # this should only fire if the code logic broke; HTTP and
            # connectivity errors should be handled within submit_payload.
            log.error("Airbrake report submission failed with exception: "
                      "{0}".format(exc))
            return False

        if not result:
            log.error("Airbrake report submission failed.")
        else:
            log.debug("Airbrake report submission successful.")

        return result

    def report(self, payload):
        """
        Submit the XML `payload` to its intended destination, thus reporting
        the error.

        Must be implemented by subclasses.

        This will be called by the Pryamid Airbrake tween.

        It should gracefully handle any exceptions that arise during its
        execution, preferrably logging them.

        """
        pass
