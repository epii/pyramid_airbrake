``pyramid_airbrake``
====================

A package for Pyramid_ that logs exceptions to the Airbrake_ application error
aggregator service via a Pyramid tween.

.. _Pyramid: http://www.pylonsproject.org/
.. _Airbrake: http://airbrakeapp.com/

Based on Steve Losh's django-hoptoad_.

.. _django-hoptoad: http://sjl.bitbucket.org/django-hoptoad/


Requirements
------------

``pyramid_airbrake`` requires:

- Python_ 2.6+
- Pyramid_ 1.2+
- A valid Airbrake_ account

.. _Python: http://www.python.org/

``pyramid_airbrake`` has not yet been tested with Python 3.x.


Installation
------------

Until ``pyramid_airbrake`` is listed on PyPI, your best bet is to clone the
source via git then, from your ``virtualenv``, run::

   $ pip install -e path/to/pyramid_aibrake

Updating to the latest version is then as simple as::

   $ cd path/to/pyramid_airbrake
   $ git pull


Setup
-----

Once ``pyramid_airbrake`` is installed, you must use the ``config.include``
mechanism to include it into your Pyramid project's configuration.  In your
Pyramid project's ``__init__.py``::

   config = Configurator(.....)
   config.include('pyramid_airbrake')

Alternately you can use the ``pyramid.includes`` configuration value in your
``.ini`` file::

   [app:myapp]
   pyramid.includes = pyramid_aibrake

Regardless of the manner of inclusion, you'll need to configure some additional
configuration settings in your ``.ini`` file before ``pyramid_airbrake`` will
run.


Configuration
-------------

For ``pyramid_airbrake`` to be able to send error reports to Airbrake_, it is
necessary to have an Airbrake_ account and obtain an Airbrake API key.  This
key must be passed to ``pyramid_airbrake`` through the ``airbrake.api_key``
configuration setting in your ``.ini`` file::

   [app:myapp]
   airbrake.api_key = 0123456789abcdefz0123456789abcde

Note that all configuration settings for ``pyramid_airbrake`` are prefixed with
``airbrake.``

By default, ``pyramid_aibrake`` will attempt to send error reports to Airbrake
over an SSL/TLS connection to protect their confidentiality.  This is the
recommended mode of operation.  However, free Airbrake accounts do not permit
reports to be submitted securely.  If you have a free account, you will need to
set the configuration setting ``airbrake.use_ssl`` to ``false``::

   [app:myapp]
   airbrake.use_ssl = false

If you do use SSL/TLS, you will need to check the value of the configuration
setting ``airbrake.ca_certs``.  This should be the path to a file containing
trusted root certificates, against which to verify the SSL/TLS connection to
Airbrake's API.  It defaults to ``/etc/ssl/certs/ca-certificates.crt``

The full list of configuration parameters are not yet documented, although an
overview may be gleaned by reading the source of
:mod:`pyramid_airbrake.settings`
