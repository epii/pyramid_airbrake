"""
This module contains the default request inspectors, at present.

"""
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
    protected = settings.get('default_inspector.protected_params') or []

    for key, value in request.params.iteritems():
        if key in protected:
            params[key] = '<protected>'
        else:
            params[key] = value

    return params

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
