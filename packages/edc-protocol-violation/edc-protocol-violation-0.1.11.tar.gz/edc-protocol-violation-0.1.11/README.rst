|pypi| |actions| |codecov| |downloads|

edc-protocol-violation
----------------------

Class to handle clinical trial protocol deviations and violations.

There are two types of this PRN form:


Protocol deviation / violation (default)
========================================
The default version requires additional details if the incident is a `violation`.


Protocol incident
=================
To use this version set:

.. code-block:: python

    settings.EDC_PROTOCOL_VIOLATION_TYPE = "incident"

Requires additional details for both types: `violation` and `deviation`.


.. |pypi| image:: https://img.shields.io/pypi/v/edc-protocol-violation.svg
    :target: https://pypi.python.org/pypi/edc-protocol-violation

.. |actions| image:: https://github.com/clinicedc/edc-protocol-violation/workflows/build/badge.svg?branch=develop
  :target: https://github.com/clinicedc/edc-protocol-violation/actions?query=workflow:build

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-protocol-violation/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-protocol-violation

.. |downloads| image:: https://pepy.tech/badge/edc-protocol-violation
   :target: https://pepy.tech/project/edc-protocol-violation
