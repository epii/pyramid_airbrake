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
    # first, filter the pyramid settings to just the ones for pyramid_airbrake
    new_settings = dict()
    f = lambda x: x.startswith(SETTINGS_PREFIX)

    for key in filter(f, settings.keys()):
        newkey = key[len(SETTINGS_PREFIX):]
        new_settings[newkey] = settings[key]

    for key in REQUIRED_SETTINGS:
        if key not in new_settings:
            raise KeyError("Compulsory setting '{0}' not found.".format(key))

    # resolve dotted python name settings
    whitelist = listwise_resolve(new_settings.get('include', ''))
    blacklist = listwise_resolve(new_settings.get('exclude',
                           'pyramid.httpexceptions.WSGIHTTPException'))

    new_settings['include'] = tuple(whitelist)
    new_settings['exclude'] = tuple(blacklist)

    return new_settings

def parse_request_params(request):
# A list of var elements describing request parameters from the query
# string, POST body, routing, and other inputs.

    return {}

def parse_request_session(request):
# A list of var elements describing session variables from the request.

    return {}

def parse_request_environment(request):
# A list of var elements describing CGI variables from the request,
# such as SERVER_NAME and REQUEST_URI.

    return {}

def parse_request_view_identifier(request):
# The component in which the error
# occurred. In model-view-controller frameworks like Rails, this should be set to
# the controller. Otherwise, this can be set to a route or other request category.
    route = request.matched_route
    if route:
        return route.name
    return 'Not a route -- maybe traversal?'
