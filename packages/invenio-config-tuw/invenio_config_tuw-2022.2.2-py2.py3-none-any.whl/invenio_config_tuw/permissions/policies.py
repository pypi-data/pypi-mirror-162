# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_rdm_records.services import RDMRecordPermissionPolicy
from invenio_rdm_records.services.generators import (
    CommunityAction,
    IfRestricted,
    RecordOwners,
    SubmissionReviewer,
)
from invenio_records_permissions.generators import (
    Admin,
    AnyUser,
    AuthenticatedUser,
    Disable,
    SuperUser,
    SystemProcess,
)
from invenio_requests.services.permissions import (
    PermissionPolicy as RequestsPermissionPolicy,
)

from .generators import (
    TrustedPublisherRecordOwners,
    TrustedRecordOwners,
    TrustedUsers,
    secret_links,
)


class TUWRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """Record permission policy of TU Wien."""

    # current state: invenio-rdm-records v0.35.21
    #
    # note: edit := create a draft from a record (i.e. putting it in edit mode),
    #               which does not imply the permission to save the edits
    # note: can_search_* is the permission for the search in general, the records
    #       (drafts) will be filtered as per can_read_* permissions
    #
    # fmt: off
    #
    # high-level permissions: not used directly (only collections for reuse);
    #                         and get more permissive from top to bottom
    # most keys were taken from invenio-rdm-records and tweaked
    # some explanations:
    # > can_basics:       gives all rights to the system, and admins
    # > can_access_draft: slightly less strict version of can_manage,
    #                     e.g. to not break user-records search
    # > can_curate:       people with curation rights (e.g. community curators)
    # > can_review:       slightly expanded from 'can_curate', can edit drafts
    can_basics             = [Admin(), SuperUser(), SystemProcess()]
    can_manage             = can_basics + [TrustedRecordOwners(), CommunityAction("curate")]         # noqa
    can_access_draft       = can_manage + [RecordOwners(), SubmissionReviewer()]                     # noqa
    can_curate             = can_manage                                   + secret_links["edit"]     # noqa
    can_review             = can_curate + [SubmissionReviewer()]                                     # noqa
    can_preview            = can_access_draft                             + secret_links["preview"]  # noqa
    can_view               = can_access_draft + [CommunityAction("view")] + secret_links["view"]     # noqa
    can_authenticated      = can_basics + [AuthenticatedUser()]                                      # noqa
    can_all                = can_basics + [AnyUser()]                                                # noqa

    # records
    can_search             = can_all                                                                                # noqa
    can_read               = [IfRestricted("record", then_=can_view, else_=can_all)] + secret_links["view_record"]  # noqa
    can_read_files         = [IfRestricted("files", then_=can_view, else_=can_all) ] + secret_links["view_files"]   # noqa
    can_create             = can_basics + [TrustedUsers()]                                                          # noqa

    # drafts
    can_search_drafts      = can_authenticated                             # noqa
    can_read_draft         = can_preview                                   # noqa
    can_draft_read_files   = can_preview                                   # noqa
    can_update_draft       = can_review                                    # noqa
    can_draft_create_files = can_review                                    # noqa
    can_draft_update_files = can_review                                    # noqa
    can_draft_delete_files = can_review                                    # noqa

    # PIDs
    can_pid_create         = can_review                                    # noqa
    can_pid_register       = can_review                                    # noqa
    can_pid_update         = can_review                                    # noqa
    can_pid_discard        = can_review                                    # noqa
    can_pid_delete         = can_review                                    # noqa

    # actions
    # > can_edit: RecordOwners is needed to not break the 'edit' button
    #             on the dashboard (UX)
    # > can_publish: TODO (trusted) submission reviewers should be allowed too
    can_edit               = can_curate + [RecordOwners()]                 # noqa
    can_delete_draft       = can_curate                                    # noqa
    can_new_version        = can_curate                                    # noqa
    can_lift_embargo       = can_manage                                    # noqa
    can_publish            = can_basics + [TrustedPublisherRecordOwners()] # noqa

    # disabled (record management in InvenioRDM goes through drafts)
    can_update             = [Disable()]                                   # noqa
    can_delete             = [Disable()]                                   # noqa
    can_create_files       = [Disable()]                                   # noqa
    can_update_files       = [Disable()]                                   # noqa
    can_delete_files       = [Disable()]                                   # noqa
    # fmt: on


class TUWRequestsPermissionPolicy(RequestsPermissionPolicy):
    """Requests permission policy of TU Wien."""

    # keep the default settings
    # this class is kept here to make overriding easier, should the need arise
    #
    # current state: invenio-requests v0.3.30


class TUWCommunitiesPermissionPolicy(CommunityPermissionPolicy):
    """Communities permission policy of TU Wien."""

    # for now, we just want to restrict the creation of communities
    #
    # current state: invenio-communities v2.8.8
    #
    # TODO: discuss who should have permissions to create communities
    #       -> new role?
    can_create = [Admin(), SuperUser(), SystemProcess()]
