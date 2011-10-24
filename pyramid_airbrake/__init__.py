from pyramid.tweens import EXCVIEW
from pyramid_airbrake.handlers import get_handler
from pyramid_airbrake.settings import parse_pyramid_settings

import logging

log = logging.getLogger(__name__)

__version__ = '0.1'
VERSION = __version__
NAME = 'pyramid_airbrake'
URL = 'http://wherever.example.com/'  # FIXME

def airbrake_tween_factory(handler, registry):
    settings = parse_pyramid_settings(registry.settings)

    if not settings['enabled']:
        return handler

    reporter = get_handler(settings)

    whitelist = settings['include']
    blacklist = settings['exclude']

    def airbrake_tween(request):
        try:
            response = handler(request)
        except whitelist:
            reporter.report(request)
            raise
        except blacklist:
            raise
        except:
            reporter.report(request)
            raise

        # TODO do we need to check for HTTP exceptions that have been returned,
        # as opposed to raised?

        return response

    return airbrake_tween


def includeme(config):
    """
    Configure an implicit tween to forward exceptions from Pyramid to Airbrake.

    By defualt, all exceptions that are not derived from
    ``pyramid.httpexceptions.WSGIHTTPException`` are forwarded.  However,
    exception classes may be included or excluded via the ``airbrake.include``
    and ``airbrake.exclude`` configuration settings.

    In case of conflict, entries in the whitelist take precedence.

    """
    config.add_tween('pyramid_airbrake.airbrake_tween_factory', under=EXCVIEW)
