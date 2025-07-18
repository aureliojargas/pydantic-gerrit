from datetime import datetime
from typing import Literal

from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit

from .accounts import AccountInfo


class GroupAuditEventInfo(BaseModelGerrit):
    """
    The GroupAuditEventInfo entity contains information about an audit event of a group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-audit-event-info
    """

    date: datetime = Field(
        description='The timestamp of the event.',
    )
    user: AccountInfo = Field(
        description='The user that did the add/remove as detailed AccountInfo entity.',
    )
    type: Literal['ADD_USER', 'REMOVE_USER', 'ADD_GROUP', 'REMOVE_GROUP'] = Field(
        description='The event type.',
    )
    member: 'AccountInfo | GroupInfo' = Field(
        description='The group member that is added/removed. If type is ADD_USER or REMOVE_USER the member is returned as detailed AccountInfo entity, if type is ADD_GROUP or REMOVE_GROUP the member is returned as GroupInfo entity. Note that the name in GroupInfo will not be set if the member group is not available.'
    )


class GroupInfo(BaseModelGerrit):
    """
    Represents information about a Gerrit group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-info
    """

    id: str
    name: str | None = Field(
        default=None,
        description='The name of the group (optional). Not set if returned in a map where the group name is used as map key. For external groups the group name is missing if there is no group backend that can resolve the group UUID. E.g. this can happen when a plugin that provided a group backend was uninstalled.',
    )
    url: str | None = Field(
        default=None,
        description='URL to information about the group (optional). Typically a URL to a web page that permits users to apply to join the group, or manage their membership.',
    )
    options: 'GroupOptionsInfo' = Field(
        # Not optional, it is always set in the API response, even when empty: {}
        description='Options of the group.',
    )
    description: str | None = Field(
        default=None,
        description='The description of the group (only for internal groups).',
    )
    group_id: int | None = Field(
        default=None,
        description='The numeric ID of the group (only for internal groups).',
    )
    owner: str | None = Field(
        default=None,
        description='The name of the owner group (only for internal groups).',
    )
    owner_id: str | None = Field(
        default=None,
        description='The URL encoded UUID of the owner group (only for internal groups).',
    )
    created_on: datetime | None = Field(
        default=None,
        description='The timestamp of when the group was created (only for internal groups).',
    )
    more_groups: bool | None = Field(
        default=None,
        alias='_more_groups',
        description='Whether the query would deliver more results if not limited (optional, only for internal groups, not set if false). Only set on the last group that is returned by a group query.',
    )
    members: list[AccountInfo] | None = Field(
        default=None,
        description='A list of AccountInfo entities describing the direct members (optional, only for internal groups). Only set if members are requested.',
    )
    includes: list['GroupInfo'] | None = Field(
        default=None,
        description='A list of GroupInfo entities describing the direct subgroups (optional, only for internal groups). Only set if subgroups are requested.',
    )


class GroupInput(BaseModelGerrit):
    """
    The GroupInput entity contains information for the creation of a new internal group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-input
    """

    name: str | None = Field(
        default=None,
        description='The name of the group (not encoded). If set, must match the group name in the URL.',
    )

    # Documentation/rest-api-groups.txt:1620:|UUID matches "^[0-9a-f]\{40\}$"|Gerrit internal group
    # Documentation/rest-api-groups.txt:1621:|UUID starts with "global:"|Gerrit system group
    # Documentation/rest-api-groups.txt:1622:|UUID starts with "ldap:"|LDAP group
    # Documentation/rest-api-groups.txt:1623:|UUID starts with "<prefix>:"|other external group
    uuid: str | None = Field(
        default=None,
        description='The UUID of the group.',
    )

    description: str | None = Field(
        default=None,
        description='The description of the group.',
    )
    visible_to_all: bool | None = Field(
        default=False,
        description='Whether the group is visible to all registered users.',
    )
    owner_id: str | None = Field(
        default=None,
        description='The URL encoded ID of the owner group. This can be a group UUID, a legacy numeric group ID or a unique group name. If not set, the new group will be self-owned.',
    )
    members: list[str] | None = Field(
        default=None,
        description='The initial members in a list of account ids.',
    )


class GroupOptionsInfo(BaseModelGerrit):
    """
    Represents options for a Gerrit group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-options-info
    """

    visible_to_all: bool | None = Field(
        default=None,
        description='Whether the group is visible to all registered users. Not set if false.',
    )


class GroupOptionsInput(BaseModelGerrit):
    """
    New options for a group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-options-input
    """

    visible_to_all: bool | None = Field(
        default=False,
        description='Whether the group is visible to all registered users.',
    )


class GroupsInput(BaseModelGerrit):
    """
    The GroupsInput entity contains information about groups that should be included into a group or that should be deleted from a group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#groups-input
    """

    one_group: str | None = Field(
        default=None,
        alias='_one_group',
        description='The id of one group that should be included or deleted.',
    )
    groups: list[str] | None = Field(
        default=None,
        description='A list of group ids that identify the groups that should be included or deleted.',
    )


class MembersInput(BaseModelGerrit):
    """
    The MembersInput entity contains information about accounts that should be added as members to a group or that should be deleted from the group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#members-input
    """

    one_member: str | None = Field(
        default=None,
        alias='_one_member',
        description='The id of one account that should be added or deleted.',
    )
    members: list[str] | None = Field(
        default=None,
        description='A list of account ids that identify the accounts that should be added or deleted.',
    )
