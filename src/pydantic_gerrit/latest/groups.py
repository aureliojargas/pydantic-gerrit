from datetime import datetime
from typing import Literal

from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit

from .accounts import AccountInfo

GroupAuditEventType = Literal['ADD_USER', 'REMOVE_USER', 'ADD_GROUP', 'REMOVE_GROUP']


class GroupAuditEventInfo(BaseModelGerrit):
    """
    The GroupAuditEventInfo entity contains information about an audit event of a group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-audit-event-info
    """

    member: 'AccountInfo | GroupInfo' = Field(
        description='The group member that is added/removed. If type is ADD_USER or REMOVE_USER the member is returned as detailed AccountInfo entity, if type is ADD_GROUP or REMOVE_GROUP the member is returned as GroupInfo entity. Note that the name in GroupInfo will not be set if the member group is not available.'
    )
    type: GroupAuditEventType = Field(
        description='The event type. ADD_USER: A user was added as member to the group. REMOVE_USER: A user member was removed from the group. ADD_GROUP: A group was included as member in the group. REMOVE_GROUP: An included group was removed from the group.',
    )
    user: AccountInfo = Field(
        description='The user that did the add/remove as detailed AccountInfo entity.',
    )
    date: datetime = Field(
        description='The timestamp of the event.',
    )


class GroupInfo(BaseModelGerrit):
    """
    The GroupInfo entity contains information about a group. This can be a Gerrit internal group, or an external group that is known to Gerrit.

    The type of a group can be deduced from the group's UUID:

        UUID matches "^[0-9a-f]{40}$" -> Gerrit internal group
        UUID starts with "global:"    -> Gerrit system group
        UUID starts with "ldap:"      -> LDAP group
        UUID starts with "<prefix>:"  -> other external group

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-info
    """

    id: str = Field(
        description='The URL encoded UUID of the group.',
    )
    name: str | None = Field(
        default=None,
        description='The name of the group. For external groups the group name is missing if there is no group backend that can resolve the group UUID. E.g. this can happen when a plugin that provided a group backend was uninstalled. (not set if returned in a map where the group name is used as map key)',
    )
    url: str | None = Field(
        default=None,
        description='URL to information about the group. Typically a URL to a web page that permits users to apply to join the group, or manage their membership.',
    )
    options: 'GroupOptionsInfo' = Field(
        # Not optional, it is always set in the API response, even when empty: {}
        description='Options of the group.',
    )
    description: str | None = Field(
        default=None,
        description='The description of the group. (only for internal groups)',
    )
    group_id: int | None = Field(
        default=None,
        description='The numeric ID of the group. (only for internal groups)',
    )
    owner: str | None = Field(
        default=None,
        description='The name of the owner group. (only for internal groups)',
    )
    owner_id: str | None = Field(
        default=None,
        description='The URL encoded UUID of the owner group. (only for internal groups)',
    )
    created_on: datetime | None = Field(
        default=None,
        description='The timestamp of when the group was created. (only for internal groups)',
    )
    more_groups: bool | None = Field(
        default=None,
        alias='_more_groups',
        description='Whether the query would deliver more results if not limited. Only set on the last group that is returned by a group query. (only for internal groups, not set if false)',
    )
    members: list[AccountInfo] | None = Field(
        default=None,
        description='A list of AccountInfo entities describing the direct members. Only set if members are requested. (only for internal groups)',
    )
    includes: list['GroupInfo'] | None = Field(
        default=None,
        description='A list of GroupInfo entities describing the direct subgroups. Only set if subgroups are requested. (only for internal groups)',
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
    uuid: str | None = Field(
        default=None,
        description='The UUID of the group. See GroupInfo docstring for the format of the UUID.',
    )
    description: str | None = Field(
        default=None,
        description='The description of the group.',
    )
    visible_to_all: bool | None = Field(
        default=False,
        description='Whether the group is visible to all registered users. (false if not set)',
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
    Options of the group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-options-info
    """

    visible_to_all: bool | None = Field(
        default=None,
        description='Whether the group is visible to all registered users. (not set if false)',
    )


class GroupOptionsInput(BaseModelGerrit):
    """
    New options for a group.

    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#group-options-input
    """

    visible_to_all: bool | None = Field(
        default=False,
        description='Whether the group is visible to all registered users. (not set if false)',
        # TODO(aj): Is it really "not set if false" or is it "false if not set" as in GroupInput.visible_to_all? Depending on the answer, also revise the default value, shouldn't it be None?
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
