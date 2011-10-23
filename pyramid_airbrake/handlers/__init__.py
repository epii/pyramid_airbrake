from pyramid_airbrake.handlers.base import BaseHandler

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
