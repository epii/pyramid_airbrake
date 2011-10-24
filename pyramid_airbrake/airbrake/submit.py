from urlparse import urlparse
import logging

import urllib3

import pyramid_airbrake

log = logging.getLogger(__name__)

def create_http_pool(settings):
    url = settings['notification_url']
    maxsize = settings['threaded.threads']  # sort of a lie, potentially
    timeout = settings['timeout']

    if settings['use_ssl']:
        ca_certs = settings['ca_certs']
        return urllib3.connection_from_url(url, maxsize=maxsize,
                                           timeout=timeout,
                                           cert_reqs='CERT_REQUIRED',
                                           ca_certs=ca_certs)

    return urllib3.connection_from_url(url, maxsize=maxsize, timeout=timeout)

def submit_payload(payload, http_pool, notification_url):
    """
    Send an XML notification to Airbrake.

    The setting `airbrake.use_ssl` controls whether an SSL connection is
    attempted and defaults to True.

    The setting `airbrake.notification_url` ...

    NB: This function must be thread-safe.

    """
    headers = {'Content-Type': 'text/xml'}
    path = urlparse(notification_url).path

    try:
        response = http_pool.urlopen('POST', path, body=payload, headers=headers)

    # TODO make these error messages more, uh, useful
    except urllib3.SSLError as exc:
        log.error("SSL Error.  Error message: '{0}'"
                  .format(exc))
        return False

    except urllib3.MaxRetryError as exc:
        log.error("Max Retries hit.  Error message: '{0}'"
                  .format(exc))
        return False

    except urllib3.TimeoutError as exc:
        log.error("Max Retries hit.  Error message: '{0}'"
                  .format(exc))
        return False

    status = response.status
    use_ssl = (http_pool.scheme == 'https')

    if status == 200:
        # submission successful
        return True

    elif status == 403 and use_ssl:
        # the account is not authorized to use SSL
        log.error("Airbrake submission returned code 403 on SSL request.  "
                  "The Airbrake account is probably not authorized to use "
                  "SSL.  Error message: '{0}'"
                  .format(response.data))

    elif status == 403 and not use_ssl:
        # the spec says 403 should only occur on SSL requests made by
        # accounts without SSL authorization, so this should never fire
        log.error("Airbrake submission returned code 403 on non-SSL "
                  "request. This is unexpected.  Error message: '{0}'"
                  .format(response.data))

    elif status == 422:
        # submitted notice was invalid; probably bad XML payload or API key
        log.error("Airbrake submission returned code 422.  Check API key. "
                  "May also be an error with {0}.  Error message: '{1}'"
                  .format(pyramid_airbrake.NAME, response.data))

    elif status == 500:
        log.error("Airbrake submission returned code 500.  This is a "
                  "problem at Airbrake's end.  Error message: '{0}'"
                  .format(response.data))

    else:
        log.error("Airbrake submission returned code '{0}', wich is not in "
                  "the Airbrake API spec.  Very strange.  Error message: '{1}'"
                  .format(status, response.data))

    return False
