from pyramid_airbrake.airbrake.apiv21 import derive_report
from pyramid_airbrake.airbrake.submit import submit_payload

import logging

log = logging.getLogger(__name__)

def get_handler(settings):
    """
    Handler factory.

    `settings` should be the result of running
    `pyramid_airbrake.util.parse_pyramid_settings` over a Pyramid deployment
    settings object.

    The handler may be chosen with the `airbrake.handler` setting.  The
    following options are valid:

    `dummy`
        Sends XML reports to the Python standard logging facility.

    `blocking`
        Sends reports to Airbrake, blocking until it is sent or the submission
        times out.

    Defaults to `dummy`.

    Note: most of this logic is currently handled in
    `pyramid_airbrake.util.parse_pyramid_settings`

    """
    return settings['handler'](settings)

class BaseHandler(object):
    def __init__(self, settings):
        self.settings = settings
        self._derive_report = derive_report  # support future API versions

    def _payload(self, request):
        """Safely generates and returns the XML string payload from `request`;
        returns None on error."""

        try:
            return self._derive_report(self.settings, request)
        except BaseException as exc:
            log.critical("Airbrake report derivation failed with exception: "
                         "{0}".format(exc))
            return None

    def _submit(self, payload):
        """Safely submits the XML `payload` to Airbrake; returns True on
        success and False on error."""

        try:
            result = submit_payload(self.settings, payload)
        except BaseException as exc:
            # this should only fire if the code logic broke; HTTP and
            # connectivity errors should be handled within submit_payload.
            log.critical("Airbrake report submission failed with exception: "
                         "{0}".format(exc))
            return False

        if not result:
            log.error("Airbrake report submission failed.")

        return result

    def report(self, request):
        """
        Prepare and submit a report based on the passed request and the current
        exception.

        Must be implemented by subclasses.

        This will be called by the Pryamid Airbrake tween.

        It should gracefully handle any exceptions that arise during its
        execution, preferrably logging them.

        """
        pass
