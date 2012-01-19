import os.path
import sys

from urlparse import urlparse

from pyramid.settings import asbool
from pyramid.settings import aslist
from pyramid.util import DottedNameResolver

# setting types
BOOL = 'bool'
DOTTED = 'dotted'  # dotted python name; will be resolved to an object
DOTTED_LIST = 'dotted_list'  # list of dotted python names
NUMERAL = 'numeral'
STR = 'string'
STR_LIST = 'string_list'  # space and/or newline seperated list XXX I think

# all pyramid_airbrake settings, their types and default values
# DOTTED and DOTTED_LIST types will be resolved to Python objects
SETTINGS_PREFIX = 'airbrake.'
SETTINGS = [
    (BOOL, 'enabled', 'yes'),
    (BOOL, 'use_ssl', 'yes'),  # ignored if notification_url is set
    (DOTTED, 'inspector.cgi_data', 'pyramid_airbrake.util.inspect_cgi_data'),
    (DOTTED, 'inspector.params', 'pyramid_airbrake.util.inspect_params'),
    (DOTTED, 'inspector.session', ''),
    (DOTTED_LIST, 'include', ''),
    (DOTTED_LIST, 'exclude', 'pyramid.httpexceptions.WSGIHTTPException'),
    (NUMERAL, 'threaded.poll_interval', 1),  # secs
    (NUMERAL, 'threaded.threads', 4),
    (NUMERAL, 'timeout', 2),  # secs
    (STR, 'api_key', ''),
    (STR, 'ca_certs', '/etc/ssl/certs/ca-certificates.crt'),
    (STR, 'notification_url', ''),  # default specified as AIRBRAKE_URL_TMPL
    (STR_LIST, 'default_inspector.protected_params', []),
    ]
REQUIRED_SETTINGS = [
    'api_key',
    ]

# for convenience, one of several keywords may be used for airbrake.handler
# instead of a full dotted name
HANDLER_KEYWORDS = {
    'blocking': 'pyramid_airbrake.handlers.blocking.BlockingHandler',
    'dummy': 'pyramid_airbrake.handlers.dummy.DummyHandler',
    'threaded': 'pyramid_airbrake.handlers.threaded.ThreadedHandler',
    }
HANDLER_DEFAULT = 'dummy'
AIRBRAKE_URL_TMPL = '{scheme}://hoptoadapp.com/notifier_api/v2/notices'

resolver = DottedNameResolver(None)

PY3 = sys.version_info[0] == 3

if PY3:
    import builtins
else:
    import __builtin__ as builtins

def resolve(key, dottedname):
    """Resolve a Python dotted name, correctly handling builtin names."""
    if dottedname in builtins.__dict__:
        if PY3:
            dottedname = 'builtins.' + dottedname
        else:
            dottedname = '__builtin__.' + dottedname

    try:
        obj = resolver.resolve(dottedname)
    except ImportError:
        raise ValueError("In setting '{0}', '{1}' could not be resolved as a "
                         "dotted Python name.".format(key, dottedname))

    return obj

def parse_pyramid_settings(pyramid_settings):
    """
    Return a pyramid_airbrake settings dictionary.

    The output will include all settings listed in the
    :const:`SETTINGS` constant, resolved to Python objects, lists, booleans, or
    integers or left as strings as appropriate for the setting.  Where a
    setting is not found in the `pyramid_settings` parameter, it will be set to
    its default value as specified in the :const:`SETTINGS` constant, unless it
    is a member of the :const:`REQUIRED_SETTINGS` constant.

    Raises `KeyError` if a compulosry setting is missing or `ValueError` if a
    dotted Python name cannot be resolved or if a setting that should represent
    a numeral cannot be coerced into one.

    Parameters

    `pyramid_settings`

        A mapping from configuration setting keys to their values.  The values
        are assumed to be strings.  Typically, this will be the deployment
        settings dictionary from a Pyramid application, retrievable from
        `request.registry.settings` in a Pyramid request.  Only settings
        with keys prefixed with 'airbrake.' will be considered, although the
        'airbrake.' prefix will be stripped off in the output dictionary's
        keys.

    """
    # first, filter the pyramid settings to just the ones for pyramid_airbrake
    settings = dict()
    f = lambda x: x.startswith(SETTINGS_PREFIX)

    for key in filter(f, pyramid_settings.keys()):
        newkey = key[len(SETTINGS_PREFIX):]
        settings[newkey] = pyramid_settings[key]

    # second, enforce the presence of required settings
    for key in REQUIRED_SETTINGS:
        if key not in settings:
            raise KeyError("Compulsory setting '{0}' not found.".format(key))

    # third, process the settings according to their type, also ensuring that
    # all defined settings were either set in the pyramid_settings dict or else
    # setting them to their default value
    for kind, key, default in SETTINGS:
        value = settings.get(key) or default

        if kind == BOOL:
            value = asbool(value)

        elif kind == DOTTED:
            if value:
                value = resolve(key, value)
            else:
                value = None

        elif kind == DOTTED_LIST:
            names = aslist(value)
            objs = [resolve(key, dottedname) for dottedname in names]
            value = tuple(objs)

        elif kind == NUMERAL:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("Value for setting '{0}' must be a numeral, "
                                 "not '{1}'.".format(key, value))
        elif kind == STR_LIST:
            value = aslist(value)

        settings[key] = value

    # handler takes either a keyword *or* a dotted Python name
    handler = settings.get('handler') or HANDLER_DEFAULT
    handler = HANDLER_KEYWORDS.get(handler) or handler
    settings['handler'] = resolve('handler', handler)

    # the use_ssl option is only applied if the notification_url is unspecified
    # otherwise, it is overidden by whether notification_url uses https
    if settings['notification_url']:
        url = settings['notification_url']
        settings['use_ssl'] = urlparse(url).scheme == 'https'

    else:
        scheme = 'https' if settings['use_ssl'] else 'http'
        url = AIRBRAKE_URL_TMPL.format(scheme=scheme)
        settings['notification_url'] = url

    # check that the airbrake.ca_certs file at least exists
    if settings['use_ssl'] and not os.path.isfile(settings['ca_certs']):
        raise ValueError("Set to use TLS/SSL but the ca_certs setting ('{0}') "
                         "does not appear to point to a file."
                         .format(settings['ca_certs']))

    return settings
