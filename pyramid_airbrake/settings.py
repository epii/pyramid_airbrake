import os.path
from urlparse import urlparse

from pyramid.httpexceptions import WSGIHTTPException
from pyramid.settings import asbool
from pyramid.settings import aslist
from pyramid.util import DottedNameResolver

import __builtin__

SETTINGS_PREFIX = 'airbrake.'
BOOL = 'bool'
DOTTED = 'dotted'  # dotted python name; will be resolved to an object
DOTTED_LIST = 'dotted_list'  # list of dotted python names
NUMERAL = 'numeral'
STR = 'str'
STR_LIST = 'str_list'  # space and/or newline seperated list XXX I think

RESOLVABLE_SETTINGS = [
    (BOOL, 'enabled', 'yes'),
    (BOOL, 'use_ssl', 'yes'),  # ignored if notification_url is set
    (DOTTED_LIST, 'include', ''),
    (DOTTED_LIST, 'exclude', 'pyramid.httpexceptions.WSGIHTTPException'),
    (DOTTED, 'inspector.params', 'pyramid_airbrake.util.inspect_params'),
    (DOTTED, 'inspector.session', 'pyramid_airbrake.util.inspect_session'),
    (DOTTED, 'inspector.cgi_data', 'pyramid_airbrake.util.inspect_cgi_data'),
    (NUMERAL, 'threaded.threads', '4'),
    (NUMERAL, 'threaded.poll_interval', '1'),  # secs
    (NUMERAL, 'timeout', '2'),  # secs
    (STR, 'notification_url', ''),  # default specified as AIRBRAKE_URL_TMPL
    (STR, 'ca_certs', '/etc/ssl/certs/ca-certificates.crt'),
    ]
REQUIRED_SETTINGS = [
    'api_key',
    ]
HANDLER_KEYWORDS = {
    'blocking': 'pyramid_airbrake.handlers.blocking.BlockingHandler',
    'dummy': 'pyramid_airbrake.handlers.dummy.DummyHandler',
    'threaded': 'pyramid_airbrake.handlers.threaded.ThreadedHandler',
    }
HANDLER_DEFAULT = 'dummy'
AIRBRAKE_URL_TMPL = '{scheme}://hoptoadapp.com/notifier_api/v2/notices'

resolver = DottedNameResolver(None)

def listwise_resolve(names):
    # TODO handle Python 3
    names = aslist(names)
    ret = []

    for name in names:
        if name in __builtin__.__dict__:
            name = '__builtin__.' + name
        ret.append(resolver.resolve(name))

    return ret

def parse_pyramid_settings(pyramid_settings):
    """Return settings prefixed with 'airbrake.', appropriately processed."""

    # first, filter the pyramid settings to just the ones for pyramid_airbrake
    settings = dict()
    f = lambda x: x.startswith(SETTINGS_PREFIX)

    for key in filter(f, pyramid_settings.keys()):
        newkey = key[len(SETTINGS_PREFIX):]
        settings[newkey] = pyramid_settings[key]

    for key in REQUIRED_SETTINGS:
        if key not in settings:
            raise KeyError("Compulsory setting '{0}' not found.".format(key))

    # second, resolve dotted python name settings
    for kind, key, default in RESOLVABLE_SETTINGS:
        value = settings.get(key, None) or default

        if kind == BOOL:
            value = asbool(value)
        elif kind == DOTTED_LIST:
            value = tuple(listwise_resolve(value))
        elif kind == DOTTED:
            if value:
                value = resolver.resolve(value)
            else:
                value = None
        elif kind == NUMERAL:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("Value for setting '{0}' must be a numeral, "
                                 "not '{1}'.".format(key, value))
        elif kind == STR_LIST:
            value = aslist(value)

        settings[key] = value

    # handler takes either a keyword *or* a dotted name
    handler = settings.get('handler', None) or HANDLER_DEFAULT
    handler = HANDLER_KEYWORDS.get(handler, handler)
    settings['handler'] = resolver.resolve(handler)

    # the use_ssl option is only applied if the notification_url is unspecified
    # otherwise, it is overidden by whether notification_url uses https
    if settings['notification_url']:
        url = settings['notification_url']
        settings['use_ssl'] = (urlparse(url).scheme == 'https')
    else:
        scheme = 'https' if settings['use_ssl'] else 'http'
        url = AIRBRAKE_URL_TMPL.format(scheme=scheme)
        settings['notification_url'] = url

    if settings['use_ssl'] and not os.path.isfile(settings['ca_certs']):
        raise ValueError("Set to use TLS/SSL but the ca_certs setting ('{0}') "
                         "does not appear to point to a file."
                         .format(settings['ca_certs']))

    return settings
