from pyramid.httpexceptions import WSGIHTTPException
from pyramid.settings import aslist
from pyramid.tweens import EXCVIEW

import logging

log = logging.getLogger(__name__)

# TODO automatically handle prepending builtins and __builtin__ to dotted
# names

def airbrake_tween_factory(handler, registry):
    get = config.registry.settings.get

    whitelist = get('airbrake.include', tuple())
    blacklist = get('airbrake.exclude', tuple())

    def airbrake_tween(request):
        try:
            response = handler(request)
        except whitelist:
            fire_airbrake()
            raise
        except blacklist:
            raise
        except:
            fire_airbrake()
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
    get = config.registry.settings.get

    whitelist = aslist(get('airbrake.include', '')))
    blacklist = aslist(get('airbrake.exclude',
                           'pyramid.httpexceptions.WSGIHTTPException'))

    config.registry.settings['airbrake.include'] = tuple(whitelist)
    config.registry.settings['airbrake.exclude'] = tuple(blacklist)

    config.add_tween('pyramid_airbrake.aibrake_tween_factory', under=EXCVIEW)
