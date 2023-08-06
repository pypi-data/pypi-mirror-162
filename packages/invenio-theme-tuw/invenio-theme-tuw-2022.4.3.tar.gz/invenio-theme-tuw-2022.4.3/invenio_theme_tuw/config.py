# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

THEME_TUW_MATOMO_ENABLED = True
"""Controls whether or not to include the JS snippet for Matomo in the base template."""

THEME_TUW_MATOMO_URL = "https://s191.dl.hpc.tuwien.ac.at/"
"""The URL under which Matomo is reachable."""

THEME_TUW_DISPLAY_STAGING_WARNING = False
"""Whether or not to display a warning that it's the staging system."""

THEME_TUW_CONTACT_EMAIL = "tudata@tuwien.ac.at"
"""The e-mail address provided as contact."""

APP_THEME = ["semantic-ui"]
"""The application theme to use."""

THEME_TUW_COMMUNITY_PERMISSION_ERROR_PARAGRAPH = None
"""Paragraph to show on the communities permission guard page."""

THEME_TUW_DEPOSIT_PERMISSION_ERROR_PARAGRAPH = None
"""Paragraph to show on the deposit permission guard page."""

THEME_TUW_FAQ_URL = "https://www.tuwien.at/en/research/rti-support/research-data/rdm-infos-tips/preserving-and-publishing/tu-data-repository-faqs"  # noqa
"""The URL to the FAQ page to be displayed."""


# Invenio-Theme
# =============
# See https://invenio-theme.readthedocs.io/en/latest/configuration.html

# Name displayed in tab
THEME_SITENAME = "TU Data Repository"

# Enabling the frontpage would collide with our custom view function
THEME_FRONTPAGE = False

# Templates
BASE_TEMPLATE = "invenio_theme_tuw/overrides/page.html"
THEME_FRONTPAGE_TEMPLATE = "invenio_theme_tuw/overrides/frontpage.html"
THEME_HEADER_TEMPLATE = "invenio_theme_tuw/overrides/header.html"
THEME_FOOTER_TEMPLATE = "invenio_theme_tuw/overrides/footer.html"
THEME_JAVASCRIPT_TEMPLATE = "invenio_theme_tuw/overrides/javascript.html"
THEME_ERROR_TEMPLATE = "invenio_theme_tuw/overrides/page_error.html"

# Header logo
THEME_LOGO = "images/TU_Signet_white.png"
INSTANCE_THEME_FILE = "less/invenio_theme_tuw/theme.less"

# Override the Invenio-OAuthClient login form
OAUTHCLIENT_SIGNUP_TEMPLATE = "invenio_theme_tuw/overrides/signup.html"
OAUTHCLIENT_LOGIN_USER_TEMPLATE = "invenio_theme_tuw/overrides/login_user.html"


# Flask-WebpackExt
# ================
# See https://flask-webpackext.readthedocs.io/en/latest/configuration.html

WEBPACKEXT_PROJECT = "invenio_theme_tuw.webpack:project"
