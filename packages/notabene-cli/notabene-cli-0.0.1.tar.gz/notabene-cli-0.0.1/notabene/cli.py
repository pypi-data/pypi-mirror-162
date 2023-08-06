#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.

It can be used as a handy facility for running the task from a command line.

.. currentmodule:: notabene.cli
.. moduleauthor:: Jeroen Peter Bos <jeroen@notabene.cloud>
"""

import notabene.template as _template
from notabene.base import base as cli

__all__ = ["cli", "_template"]
