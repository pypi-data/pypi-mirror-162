# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask_login import current_user
from flask_principal import RoleNeed, UserNeed
from invenio_rdm_records.services.generators import SecretLinks
from invenio_records_permissions.generators import Generator


class TrustedUsers(Generator):
    """Allows users with the "trusted-user" role."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        return [RoleNeed("trusted-user")]


class RecordOwnersWithRole(Generator):
    """Allows record owners with a given role."""

    def __init__(self, role_name, exclude=True):
        """Constructor."""
        super().__init__()
        self.role_name = role_name
        self.exclude = exclude

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        if record is None:
            if (
                bool(current_user)
                and not current_user.is_anonymous
                and current_user.has_role(self.role_name)
            ):
                return [UserNeed(current_user.id)]
            else:
                return []

        return [
            UserNeed(owner.owner_id)
            for owner in record.parent.access.owners
            if owner.resolve().has_role(self.role_name)
        ]

    def excludes(self, **kwargs):
        """Explicit excludes."""
        if not self.exclude:
            return super().excludes(**kwargs)

        elif (
            bool(current_user)
            and not current_user.is_anonymous
            and not current_user.has_role(self.role_name)
        ):
            return [UserNeed(current_user.id)]

        return []


def TrustedRecordOwners(exclude=False):
    """Allows record owners with the "trusted-user" role."""
    return RecordOwnersWithRole("trusted-user", exclude=exclude)


def TrustedPublisherRecordOwners(exclude=False):
    """Allows record owners with the "trusted-publisher" role."""
    return RecordOwnersWithRole("trusted-publisher", exclude=exclude)


secret_links = {
    "edit": [SecretLinks("edit")],
    "view": [SecretLinks("edit"), SecretLinks("view")],
    "view_record": [SecretLinks("edit"), SecretLinks("view"), SecretLinks("record")],
    "view_files": [SecretLinks("edit"), SecretLinks("view"), SecretLinks("files")],
    "preview": [SecretLinks("edit"), SecretLinks("preview")],
}
