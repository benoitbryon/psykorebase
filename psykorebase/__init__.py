# -*- coding: utf-8 -*-
"""Psykorebase package: perform merge-based rebases."""


pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('psykorebase')

#: Module version, as defined in PEP-0396.
__version__ = distribution.version
