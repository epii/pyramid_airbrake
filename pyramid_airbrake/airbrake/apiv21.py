import traceback
import sys

from xml.etree import ElementTree as ET

import pyramid_airbrake

def derive_report(settings, request):
    """
    Returns, as a string, an XML Airbrake payload.

    Implements the Airbrake API version 2.1.

    """
    # API reference:
    # http://help.airbrake.io/kb/api-2/notifier-api-version-21
    notice = ET.Element('notice')  # the root element

    # /notice/@version ; required
    notice.set('version', '2.1')

    # /notice/api-key ; required
    api_key = ET.SubElement(notice, 'api-key')
    api_key.text = settings['api_key']


    # /notice/notifier
    notifier = ET.SubElement(notice, 'notifier')

    # /notice/notifier/name ; required
    name = ET.SubElement(notifier, 'name')
    name.text = pyramid_airbrake.NAME

    # /notice/notifier/version ; required
    version = ET.SubElement(notifier, 'version')
    version.text = pyramid_airbrake.VERSION

    # /notice/notifier/url ; required
    url = ET.SubElement(notifier, 'url')
    url.text = pyramid_airbrake.URL


    # /notice/error
    error = ET.SubElement(notice, 'error')

    # I believe local variable assignment is okay, circular-reference wise, as
    # the local variable trace is in a different function to the one handling
    # the exception (i.e. the func with the relevant except statement).
    cls, exc, trace = sys.exc_info()

    # /notice/error/class ; required
    err_class = ET.SubElement(error, 'class')
    err_class.text = cls.__name__

    # /notice/error/message
    if exc.message:
        message = ET.SubElement(error, 'message')
        message.text = str(exc.message)

    # /notice/error/backtrace/line ; required
    backtrace = ET.SubElement(error, 'backtrace')

    tb = traceback.extract_tb(trace)
    if not tb:
        tb = [('unknown', 0, 'unknown', None)]

    for filename, lineno, funcname, text in reversed(tb):
        ET.SubElement(backtrace, 'line', attrib={
            'file': str(filename),
            'number': str(lineno),
            'method': str(funcname),
            })


    # /notice/request
    req = ET.SubElement(notice, 'request')

    # /notice/request/url ; required (if request)
    url = ET.SubElement(req, 'url')
    url.text = request.url

    # /notice/request/component ; required (if request)
    component = ET.SubElement(req, 'component')
    component.text = inspect_view_identifier(settings, request)

    # /notice/request/action
    action = ET.SubElement(req, 'action')
    action.text = request.method  # XXX this is probably wrong


    # //var
    def add_vars(parent, vardict):
        for key, value in vardict.iteritems():
            child = ET.SubElement(parent, 'var', {'key': str(key)})
            child.text = str(value)

    # /notice/request/params/var
    # /notice/request/session/var
    # /notice/request/cgi-data/var
    for node_name in ('params', 'session', 'cgi-data'):

        inspector = settings['inspector.' + node_name]
        vardict = inspector(settings, request)

        if vardict:
            node = ET.SubElement(req, node_name)
            add_vars(node, vardict)


    # /notice/server-environment
    server_env = ET.SubElement(notice, 'server-environment')

    # /notice/server-environment/project-root
    project_root = ET.SubElement(server_env, 'project-root')
    project_root.text = sys.path[0]  # TODO come up with something better?

    # /notice/server-environment/environment-name ; required
    env_name = ET.SubElement(server_env, 'environment-name')
    env_name.text = settings.get('env_name', 'unspecified')

    # /notice/server-environment/app-version
    if 'app_version' in settings:
        app_version = ET.SubElement(server_env, 'app-version')
        app_version.text = settings['app_version']


    return ET.tostring(notice)
