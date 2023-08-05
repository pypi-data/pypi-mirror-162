pygitsync
=========

A utility to poll a remote git repository and maintain local state according
simple rules such as the HEAD of a specified branch, or the latest tag
conforming to a regular expression.

.. contents::

.. section-numbering::


Installation
------------

The ``pygitsync`` package is available from PyPI. Installing into a virtual
environment is recommended.

.. code-block::

   python3 -m venv .venv; .venv/bin/pip install pygitsync

