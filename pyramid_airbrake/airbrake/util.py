from pyramid.httpexceptions import WSGIHTTPException
from pyramid.settings import aslist
from pyramid.util import DottedNameResolver

import __builtin__

SETTINGS_PREFIX = 'airbrake.'
REQUIRED_SETTINGS = [
        'api_key',
        ]

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
    whitelist = listwise_resolve(new_settings.get('include', ''))
    blacklist = listwise_resolve(new_settings.get('exclude',
                           'pyramid.httpexceptions.WSGIHTTPException'))

    new_settings['include'] = tuple(whitelist)
    new_settings['exclude'] = tuple(blacklist)

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
