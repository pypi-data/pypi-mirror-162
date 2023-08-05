# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions."""

from logging.handlers import SMTPHandler

from flask_principal import Identity
from flask_security import current_user
from invenio_access import any_user
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_accounts.models import User

# Utilities for internal use
# --------------------------


def get_user_by_username(username):
    """Get the user identified by the username."""
    profile = User.query.filter(User.username == username).one_or_none()

    if profile is not None:
        return profile.user

    return None


def get_user(identifier):
    """Get the user identified by the given ID, email or username."""
    user = current_accounts.datastore.get_user(identifier)
    if user is None:
        get_user_by_username(identifier)

    return user


def get_identity_for_user(user):
    """Get the Identity for the user specified via email, ID or username."""
    identity = None
    if user is not None:
        # note: this seems like the canonical way to go
        #       'as_user' can be either an integer (id) or email address
        u = get_user(user)
        if u is not None:
            identity = get_identity(u)
        else:
            raise LookupError("user not found: %s" % user)

    if identity is None:
        identity = Identity(1)

    identity.provides.add(any_user)
    return identity


# Utilities for invenio configuration
# -----------------------------------


def check_user_email_for_tuwien(user):
    """Check if the user's email belongs to TU Wien (but not as a student)."""
    domain = user.email.split("@")[-1]
    return domain.endswith("tuwien.ac.at") and "student" not in domain


def current_user_as_creator():
    """Use the currently logged-in user to populate a creator in the deposit form."""
    profile = current_user.user_profile or {}
    if profile.get("full_name") is None:
        return []

    name_parts = profile["full_name"].split()
    if len(name_parts) <= 1:
        return []

    first_name = " ".join(name_parts[:-1])
    last_name = name_parts[-1]
    full_name = "{}, {}".format(last_name, first_name)
    # TODO parse affiliation from user profile
    creator = {
        "affiliations": [
            {
                "identifiers": [{"identifier": "04d836q62", "scheme": "ror"}],
                "name": "TU Wien, Vienna, Austria",
            }
        ],
        "person_or_org": {
            "family_name": last_name,
            "given_name": first_name,
            "identifiers": [],
            "name": full_name,
            "type": "personal",
        },
    }

    return [creator]


# "Dirty-Hack" Utilities
# -----------------------------------


def remove_duplicate_smtp_handlers(logger):
    """Checks if duplicate SMTP handlers are registered on the provided logger.
    
    NOTE: 
    **The problem**: The current extension will be registered for both apps (UI and API)
    when running the instance locally. Thus, two identical SMTP handlers will be registered,
    resulting in duplicate emails.
    **The solution**: The function will remove the duplicate SMTPHandler dynamically to
    avoid sending duplicate emails for the same unhandled exception occuring.
    In containerized mode, it will do nothing because one handler will be registered for 
    each web-app (ui & api).
    This function doesn't eliminate more that 2 identical SMTP handlers.
    """
    # TODO: This function is a dirty workaround.
    # Alternatives:
    # * Splitting the current extension into separate ones (for the UI and API) 
    #   should eliminate the need for it.
    # * Check somehow if the app is running as a container or locally (?)

    # We don't mutate the handlers while iterating.
    # See: https://stackoverflow.com/questions/7484454/removing-handlers-from-pythons-logging-loggers
    flag = seen = False
    for index, handler in enumerate(logger.handlers):
        if isinstance(handler, SMTPHandler) and handler.level == 40:
            if not seen:
                seen = True
                continue
            flag, pos = True, index

    # Remove the handler after the duplicate has been found.
    if flag:
        logger.removeHandler(logger.handlers[pos])
    return flag
    