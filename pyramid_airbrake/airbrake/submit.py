import logging
import urllib2

import pyramid_airbrake

log = logging.getLogger(__name__)

AIRBRAKE_URL_TMPL = '{scheme}://hoptoadapp.com/notifier_api/v2/notices'

# XXX oh my goodness, urllib2 does not verify certificates, nor does it provide
# an easy way to do so
# SSL is useless until a work-around is implemented.

def submit_payload(settings, payload, timeout=5):
    """
    Send an XML notification to Airbrake.

    The setting `airbrake.use_ssl` controls whether an SSL connection is
    attempted and defaults to True.

    The setting `airbrake.notification_url`

    """
    headers = {'Content-Type': 'text/xml'}

    notification_url = settings.get('notification_url', None)

    if notification_url:
        use_ssl = notification_url.startswith('https://')
    else:
        use_ssl = settings.get('use_ssl', True)
        scheme = 'https' if use_ssl else 'http'
        notification_url = AIRBRAKE_URL_TMPL.format(scheme=scheme)

    req = urllib2.Request(notification_url, payload, headers)

    try:
        response = urllib2.urlopen(req, timeout=timeout)
        return True
        # should we check that this is 200 OK (as opposed to some other 2xx)?

    except urllib2.HTTPError as exc:
        status = exc.code

        if status == 403 and use_ssl:
            # the account is not authorized to use SSL
            log.error("Airbrake submission returned code 403 on SSL request.  "
                      "The Airbrake account is probably not authorized to use "
                      "SSL.  Error message: '{0}'"
                      .format(exc.read()))

        if status == 403 and not use_ssl:
            # the spec says 403 should only occur on SSL requests made by
            # accounts without SSL authorization, so this should never fire
            log.error("Airbrake submission returned code 403 on non-SSL "
                      "request. This is unexpected.  Error message: '{0}'"
                      .format(exc.read()))

        if status == 422:
            # submitted notice was invalid; probably bad XML payload or API key
            log.error("Airbrake submission returned code 422.  Check API key. "
                      "May also be an error with {0}.  Error message: '{1}'"
                      .format(pyramid_airbrake.NAME, exc.read()))

        if status == 500:
            log.error("Airbrake submission returned code 500.  This is a "
                      "problem at Airbrake's end.  Error message: '{0}'"
                      .format(exc.read()))

    except urllib2.URLError as exc:
        log.error("Unable to connect to Airbreak; URL: {0}; Error: '{1}'"
                  .format(notification_url, exc.reason))

    return False
