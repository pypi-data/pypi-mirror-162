# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_oauth2server = LocalProxy(
    lambda: current_app.extensions["invenio-oauth2server"]
)
"""Return current state of the OAuth2 server extension."""
