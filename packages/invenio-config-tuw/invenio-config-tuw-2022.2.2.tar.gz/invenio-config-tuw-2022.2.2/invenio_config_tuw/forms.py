# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask import current_app, url_for
from flask_babelex import gettext as _
from markupsafe import Markup
from werkzeug.local import LocalProxy
from wtforms import BooleanField, Form, HiddenField, validators
from wtforms.fields.core import FormField

_security = LocalProxy(lambda: current_app.extensions["security"])


def tuw_registration_form(*args, **kwargs):
    """Create the registration form for TU Wien.

    This registration form will only hold values but not display any input fields,
    because we get all our information from the TUW SSO/Keycloak.
    The form's structure should reflect that of the ``User`` model.

    Note: Invenio-OAuthClient 2.0 tweaked the workings of the registration a bit;
    now the precedence mask is applied to values from the user's input in the form,
    the result of which is then fed back to the form (for validation, I assume),
    which in turn is fetched again and used to populate the user account.
    This means that we have to actually hold information in the forms and can't
    just set every field to ``None``.
    """

    terms_of_use_file = _("TU_Data_Terms_of_Use_20210511_en.pdf")
    terms_of_use_url = url_for("static", filename=(f"documents/{terms_of_use_file}"))
    message = Markup(
        f"Accept the <a href='{terms_of_use_url}' target='_blank'>Terms and Conditions</a>"  # noqa
    )

    class UserProfileForm(Form):
        """Form for the user profile."""

        full_name = HiddenField()
        affiliations = HiddenField()

    class UserRegistrationForm(_security.confirm_register_form):
        """Form for the basic user information."""

        email = HiddenField()
        username = HiddenField()
        user_profile = FormField(UserProfileForm, separator=".")
        password = None
        recaptcha = None
        profile = None  # disable the default 'profile' form from invenio
        submit = None  # defined in the template
        terms_of_use = BooleanField(message, [validators.required()])

        def to_dict(self):
            """Turn the form into a dictionary."""
            return {
                "email": self.email.data,
                "username": self.username.data,
                "password": None,
                "user_profile": {
                    "full_name": self.user_profile.full_name.data,
                    "affiliations": self.user_profile.affiliations.data,
                },
            }

    return UserRegistrationForm(*args, **kwargs)
