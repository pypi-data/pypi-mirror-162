# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module containing some customizations and configuration for TU Wien."""

from functools import partial
from logging.handlers import SMTPHandler

from flask_security.signals import user_registered
from invenio_mail import InvenioMail

from . import config
from .auth.utils import auto_trust_user
from .formatters import CustomFormatter
from .permissions import TUWCommunitiesPermissionPolicy
from .utils import remove_duplicate_smtp_handlers


@user_registered.connect
def auto_trust_new_user(sender, user, **kwargs):
    # NOTE: 'sender' and 'kwargs' are ignored, but they're required to match the
    #       expected function signature
    # NOTE: this function won't be called when a user is created via the CLI
    #       ('invenio users create'), because it doesn't send the 'user_registered'
    #       signal
    auto_trust_user(user)


class InvenioConfigTUW(object):
    """Invenio-Config-TUW extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self._overrides = set()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-config-tuw"] = self
        self.override_communities_permissions(app)
        # Ensure that invenio_mail is registered in the app.
        if "invenio-mail" not in app.extensions:
            InvenioMail(app)
        # Email error handling should occur only in production mode.
        if not app.debug and not app.testing:
            self.register_smtp_error_handler(app)
            remove_duplicate_smtp_handlers(app.logger)

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        for k in dir(config):
            if len(k.replace("_", "")) >= 3 and k.isupper():
                app.config.setdefault(k, getattr(config, k))

        # the datacenter symbol seems to be the username for DataCite Fabrica
        if app.config.get("DATACITE_ENABLED", False):
            key = "DATACITE_DATACENTER_SYMBOL"
            if not app.config.get(key, None):
                app.config[key] = app.config["DATACITE_USERNAME"]

    def override_communities_permissions(self, app):
        """Override permission policy class for communities."""
        # TODO change this as soon as Invenio-Communities allows to do it via config
        key = "invenio-communities"
        if key in self._overrides:
            return

        communities = app.extensions.get(key, None)
        if communities is not None and communities.service is not None:
            # override the permission policy class for all communities services
            svc = communities.service
            svc.config.permission_policy_cls = TUWCommunitiesPermissionPolicy
            svc.files.config.permission_policy_cls = TUWCommunitiesPermissionPolicy
            svc.members.config.permission_policy_cls = TUWCommunitiesPermissionPolicy
            self._overrides.add(key)
            app.logger.debug("Communities permissions overridden.")
        else:
            # if the override failed, schedule it before the first request
            app.logger.warning(
                "Could not override communities permissions: extension not loaded!"
            )
            override_func = partial(self.override_communities_permissions, app)
            app.before_first_request_funcs.append(override_func)

    def register_smtp_error_handler(self, app):
        """Register email error handler to the application."""
        # Check if mail server and admin(s) email(s) are present in the config
        # If not raise a warning
        if app.config.get("MAIL_SERVER") and app.config.get("MAIL_ADMIN"):
            # Configure Auth
            auth = None
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            # Configure TLS
            secure = None
            if app.config.get("MAIL_USE_TLS"):
                secure = ()

            # Initialize SMTP Handler
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config.get("MAIL_PORT", 25)),
                fromaddr=app.config["SECURITY_EMAIL_SENDER"],
                toaddrs=app.config["MAIL_ADMIN"],
                subject=app.config["THEME_SITENAME"] + " - Failure",
                credentials=auth,
                secure=secure
            )
            # level 40 is for ERROR. See python's logging for further mappings.
            mail_handler.setLevel(40)
            # add custom formatter
            mail_handler.setFormatter(CustomFormatter())
            # Attach to the application
            app.logger.addHandler(mail_handler)
        else:
            app.logger.warning(
                "Mail configuration missing: SMTP error handler not registered!"
            )
