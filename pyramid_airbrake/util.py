from pyramid.httpexceptions import WSGIHTTPException
from pyramid.settings import asbool
from pyramid.settings import aslist
from pyramid.util import DottedNameResolver

import __builtin__

SETTINGS_PREFIX = 'airbrake.'
BOOL = 'bool'
DOTTED = 'dotted'  # dotted python name; will be resolved to an object
DOTTED_LIST = 'dotted_list'  # list of dotted python names
STR = 'str'
STR_LIST = 'str_list'  # space and/or newline seperated list XXX I think

RESOLVABLE_SETTINGS = [
    (BOOL, 'use_ssl', 'yes'),
    (DOTTED_LIST, 'include', ''),
    (DOTTED_LIST, 'exclude', 'pyramid.httpexceptions.WSGIHTTPException'),
    (DOTTED, 'inspector.params', 'pyramid_airbrake.util.inspect_params'),
    (DOTTED, 'inspector.session', 'pyramid_airbrake.util.inspect_session'),
    (DOTTED, 'inspector.cgi_data', 'pyramid_airbrake.util.inspect_cgi_data'),
    ]
REQUIRED_SETTINGS = [
    'api_key',
    ]
HANDLER_KEYWORDS = {
    'blocking': 'pyramid_airbrake.handlers.blocking.BlockingHandler',
    'dummy': 'pyramid_airbrake.handlers.dummy.DummyHandler',
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
        elif kind == STR_LIST:
            value = aslist(value)

        new_settings[key] = value

    # handler takes either a keyword *or* a dotted name
    handler = new_settings.get('handler', None) or HANDLER_DEFAULT
    handler = HANDLER_KEYWORDS.get(handler, handler)
    new_settings['handler'] = resolver.resolve(handler)

    return new_settings

def inspect_params(settings, request):
    """
    Returns a dict of scrubbed GET and POST parameters from the request.

    Any value whose key appears in the airbrake.protected_params setting is
    changed to '<protected>'.

    Note that this function implementation consults only request.params, not
    request.GET or request.POST.

    Override with `airbrake.inspector.params`.

    """
    params = dict()
    protected = settings.get('protected_params', [])

    for key, value in request.params.iteritems():
        # TODO confirm the best way to handle Unicode in XML
        key = key.encode('utf-8')
        value = value.encode('utf-8')

        if key in protected:
            params[key] = '<protected>'
        else:
            params[key] = value

    return params

def inspect_session(settings, request):
    """Returns an empty dict; override with `airbrake.inspector.session`."""
    return dict()

DEFAULT_ENV_VARS = [
    'HTTP_HOST',
    'HTTP_REFERER',
    'HTTP_USER_AGENT',
    ]

def inspect_cgi_data(settings, request):
    """
    Returns a dict of several environment variables.

    Override the default environment variables with `airbrake.environment_vars`.

    Override entirely with `airbrake.inspector.cgi_data'.

    """
    env = dict()
    keys = settings.get('environment_vars', None) or DEFAULT_ENV_VARS

    for key in keys:
        if key in request.environ:
            env[key] = request.environ[key]

    return env

def inspect_view_identifier(settings, request):
    """
    Return the name of the view.

    However, Pyramid doesn't seem to make that easy, especially for traversal,
    so for now any reasonably unique identifier will suffice.

    """
    route = request.matched_route
    if route:
        return route.name
    return 'Not a route -- maybe traversal?'
    # TODO
