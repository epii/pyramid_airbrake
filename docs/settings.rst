.. _settings-page:

Settings
========

.. warning:: Not all settings have been adequately tested yet; if in doubt,
             just stick to those under :ref:`main-page-settings` on the main
             page.

.. automodule:: pyramid_airbrake.settings


tries to make it easy to customize a variety of error
report details by inserting custom `inspectors`

General
-------

These settings configure basic attributes of ``pyramid_airbrake``


``airbrake.enable``
^^^^^^^^^^^^^^^^^^^

Type: Boolean

Default: ``true``

This setting enables or disables the operation of ``pyramid_airbrake``.  If
disabled, then the airbrake tween factory does not add the ``pyramid_airbrake``
tween code to the Pyramid handler.  This may be useful if ``pyramid_airbrake``
has been added to a Pyramid app through the imperative ``config.include()``
method but you wish to turn it on or off through your configuration file.


``airbrake.api_key``
^^^^^^^^^^^^^^^^^^^^

See: :ref:`main-page-settings` on the main page.


``airbrake.use_ssl``
^^^^^^^^^^^^^^^^^^^^

See: :ref:`main-page-settings` on the main page.


``airbrake.ca_certs``
^^^^^^^^^^^^^^^^^^^^^

See: :ref:`main-page-settings` on the main page.


``airbrake.exclude``
^^^^^^^^^^^^^^^^^^^^

Type: Space-separated List of Dotted Python Names

Default: ``pyramid.httpexceptions.WSGIHTTPException``

A list of exception classes that will be ignored.  That is, if the application
raises an exception that is an instance of one of the listed classes, or an
instance of a class that inherits from any of these classes, then the exception
will not submitted to Airbrake.


``airbrake.include``
^^^^^^^^^^^^^^^^^^^^

Type: Space-seperated List of Dotted Python Names

Default: `None`

A list of exception classes that will not be ignored, even though they appear
in ``airbrake.exclude`` or inherit from a class that does.

For example, to submit only ``KeyError`` exceptions to airbrake, you could set
``airbrake.exclude`` to ``Exception`` and then set ``airbrake.include`` to
``KeyError``.



Error Submission
----------------


``airbrake.notification_url``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: String

Default: ``https://hoptoadapp.com/notifier_api/v2/notices``

This sets the URL to which error notifications are submitted.  You should not
need to change this unless you wish to test the operation of
``pyramid_airbrake`` against your own endpoint or if Airbrake deprecates the
default setting (which is unlikely).


``airbrake.handler``
^^^^^^^^^^^^^^^^^^^^

Type: Keyword or Dotted Python Name

Default: ``threaded``

This chooses the handler that will submit the generated XML error report to the
Airbrake API endpoint.

-  ``dummy``
-  ``blocking``
-  ``threaded``


``airbrake.threaded.poll_interval``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Numeral

Default: ``1``



``airbrake.threaded.threads``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Numeral

Default: ``4``



``airbrake.timeout``
^^^^^^^^^^^^^^^^^^^^

Type: Numeral

Default: ``2``




Inspectors
----------


``airbrake.inspector.cgi_data``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Dotted Python Name

Default: ``pyramid_airbrake.util.inspect_cgi_data``



``airbrake.inspector.params``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Dotted Python Name

Default: ``pyramid_airbrake.util.inspect_params``



``airbrake.default_inspector.protected_params``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Space-separated List of Strings

Default: `None`



``airbrake.inspector.session``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Type: Dotted Python Name

Default: `None`


