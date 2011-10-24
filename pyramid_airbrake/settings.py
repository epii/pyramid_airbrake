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
    (STR, 'notification_url', ''),  # default specified in airbrake.submit
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

def parse_pyramid_settings(settings):
    """Return settings prefixed with 'airbrake.', appropriately processed."""

    # first, filter the pyramid settings to just the ones for pyramid_airbrake
    new_settings = dict()
    f = lambda x: x.startswith(SETTINGS_PREFIX)

    for key in filter(f, settings.keys()):
        newkey = key[len(SETTINGS_PREFIX):]
        new_settings[newkey] = settings[key]

    for key in REQUIRED_SETTINGS:
        if key not in new_settings:
            raise KeyError("Compulsory setting '{0}' not found.".format(key))

    # second, resolve dotted python name settings
    for kind, key, default in RESOLVABLE_SETTINGS:
        value = new_settings.get(key, None) or default

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

        new_settings[key] = value

    # handler takes either a keyword *or* a dotted name
    handler = new_settings.get('handler', None) or HANDLER_DEFAULT
    handler = HANDLER_KEYWORDS.get(handler, handler)
    new_settings['handler'] = resolver.resolve(handler)

    return new_settings
