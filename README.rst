========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-rh-nexttask/badge/?style=flat
    :target: https://readthedocs.org/projects/python-rh-nexttask
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/sathlan/python-rh-nexttask.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/sathlan/python-rh-nexttask

.. |codecov| image:: https://codecov.io/github/sathlan/python-rh-nexttask/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/sathlan/python-rh-nexttask

.. |version| image:: https://img.shields.io/pypi/v/rh-nexttask.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/rh-nexttask

.. |commits-since| image:: https://img.shields.io/github/commits-since/sathlan/python-rh-nexttask/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/sathlan/python-rh-nexttask/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/rh-nexttask.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/rh-nexttask

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rh-nexttask.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/rh-nexttask

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/rh-nexttask.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/rh-nexttask


.. end-badges

Next task for redhatter working on Openstack upstream and downstream.

* Free software: BSD license

Installation
============

::

    pip install rh-nexttask

Documentation
=============

https://python-rh-nexttask.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
