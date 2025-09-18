from collections.abc import Generator
from typing import Any, cast

import pytest

from pydantic_gerrit.v3_12.accounts import AccountInfo
from pydantic_gerrit.v3_12.groups import (
    GroupAuditEventInfo,
    GroupInfo,
    GroupInput,
    GroupOptionsInfo,
    GroupOptionsInput,
    GroupsInput,
    MembersInput,
)
from tests.helpers import TESTS_RESPONSE_DIR, api_call, dump_json_to_file, parse_response_text
from tests.test_accounts import get_account

# These constants are set in setup_gerrit_groups_test()
GROUP1: GroupInfo
GROUP2: GroupInfo
GROUP3: GroupInfo
GROUP4: GroupInfo
ADMIN_ACCOUNT: AccountInfo


def get_group(name_or_id: str, *, includes: bool = False, members: bool = False) -> GroupInfo | None:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#get-group
    """
    params = [('query', name_or_id)]
    if includes:
        params.append(('o', 'INCLUDES'))
    if members:
        params.append(('o', 'MEMBERS'))
    response = api_call('groups/', params=params)
    parsed_response: list[Any] = parse_response_text(response.text)
    if parsed_response:
        return GroupInfo.model_validate(parse_response_text(response.text)[0])
    return None


def create_group(name: str, input_: GroupInput | None = None) -> GroupInfo:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#create-group
    """
    if group := get_group(name):
        return group

    # direct validation: GroupInput
    data = input_.model_dump(mode='json') if input_ else {}
    response = api_call(f'groups/{name}', method='PUT', data=data)
    return GroupInfo.model_validate(parse_response_text(response.text))


def add_subgroups(group_id: str, input_: GroupsInput) -> list[GroupInfo]:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#add-subgroups
    """
    response = api_call(f'groups/{group_id}/groups', method='POST', data=input_.model_dump(mode='json'))
    parsed_response: list[Any] = parse_response_text(response.text)
    return [GroupInfo.model_validate(x) for x in parsed_response]


def add_members(group_id: str, input_: MembersInput) -> list[AccountInfo]:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#_add_group_members
    """
    response = api_call(f'groups/{group_id}/members', method='POST', data=input_.model_dump(mode='json'))
    parsed_response: list[Any] = parse_response_text(response.text)
    return [AccountInfo.model_validate(x) for x in parsed_response]


def remove_members(group_id: str, input_: MembersInput) -> None:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#remove-group-members
    """
    api_call(f'groups/{group_id}/members.delete', method='POST', data=input_.model_dump(mode='json'))


# This raises "Deletion of Group is not enabled"
# Must edit `gerrit.config`, setting `gerrit.enableGroupDeletion` to true:
# git config -f /var/gerrit/etc/gerrit.config gerrit.enableGroupDeletion true
# /var/gerrit/bin/gerrit.sh restart
# but support for this was added in Nov 2024, so it won't work on older versions, we can't rely on that:
# 8463fb9c9d90dd8a8792cc861a84796528b893b1
def delete_group(id_: str) -> None:
    """
    https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#delete-group
    """
    api_call(f'groups/{id_}', method='DELETE')


@pytest.fixture(scope='session')
def setup_gerrit_groups_test() -> Generator[None]:
    """
    Fixture to set up specific environment for group tests.
    """
    # Cannot delete groups on versions previous to Nov 2024, so any adding is permanent
    # https://gerrit-review.googlesource.com/c/gerrit/+/431917

    global ADMIN_ACCOUNT, GROUP1, GROUP2, GROUP3, GROUP4  # noqa: PLW0603

    # Using `self` because we run the tests as the Administrator user
    ADMIN_ACCOUNT = cast('AccountInfo', get_account(account_id='self'))

    # Groups already available in a Gerrit fresh install
    GROUP1 = cast('GroupInfo', get_group(name_or_id='Administrators'))
    GROUP2 = cast('GroupInfo', get_group(name_or_id='Service Users'))
    GROUP3 = cast('GroupInfo', get_group(name_or_id='Blocked Users'))

    # Ideally, we would be using only the default groups to test the API, but the only way of
    # testing GroupInput is creating a group.
    GROUP4 = create_group(
        name='test-group-4',
        input_=GroupInput(description='test-group-4 description', uuid='4' * 40, visible_to_all=False),
    )

    # Setup ended, now the tests will be run
    yield

    # Teardown code here
    print('No teardown')  # noqa: T201


# Apply the setup fixture automatically to all tests in this module
pytestmark = pytest.mark.usefixtures('setup_gerrit_groups_test')


def test_group_options() -> None:
    group_id = GROUP4.group_id
    input_ = GroupOptionsInput(visible_to_all=True)  # direct validation: GroupOptionsInput
    response = api_call(f'groups/{group_id}/options', method='PUT', data=input_.model_dump(mode='json'))
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_json_to_file(parsed_response, TESTS_RESPONSE_DIR / 'group-options.json')

    validated = GroupOptionsInfo.model_validate(parsed_response)
    assert validated.visible_to_all is True


def test_groups_input() -> None:  # direct validation: GroupsInput
    using_groups = add_subgroups(group_id=GROUP4.id, input_=GroupsInput(groups=[GROUP1.id]))
    assert [x for x in using_groups if x.id == GROUP1.id]

    using_one_group = add_subgroups(group_id=GROUP4.id, input_=GroupsInput(_one_group=GROUP2.id))
    assert [x for x in using_one_group if x.id == GROUP2.id]


def test_members_input() -> None:  # direct validation: MembersInput
    # Since in this test we're calling get_group() with members=True, we're also testing AccountInfo
    # indirect validation: AccountInfo

    admin_email = ADMIN_ACCOUNT.email
    assert admin_email is not None

    # Administrator is automatically added to our custom group when we created it in the setup.
    # Let's just make sure it's there now.
    group4 = get_group(name_or_id=GROUP4.id, members=True)
    assert group4 is not None
    assert group4.members == [ADMIN_ACCOUNT]

    # Now remove it using MembersInput(members=)
    remove_members(group_id=group4.id, input_=MembersInput(members=[admin_email]))
    group4 = get_group(name_or_id=GROUP4.id, members=True)
    assert group4 is not None
    assert group4.members == []

    # Now readd it using MembersInput(_one_member=)
    add_members(group_id=group4.id, input_=MembersInput(_one_member=admin_email))
    group4 = get_group(name_or_id=GROUP4.id, members=True)
    assert group4 is not None
    assert group4.members == [ADMIN_ACCOUNT]


def test_group_info() -> None:
    response = api_call('groups')
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_json_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups.json')

    validated: list[GroupInfo] = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.options is not None for x in validated)  # always set, even when empty
    assert any(x.options for x in validated)  # indirect validation: GroupOptionsInfo
    assert all(x.members is None for x in validated)  # not set by default
    assert all(x.includes is None for x in validated)  # not set by default
    assert all(x.more_groups is None for x in validated)  # not set by default
    # `name` is not set if returned in a map where the group name is used as map key (our case here)
    assert all(x.name is None for x in validated)


def test_group_info_plus_members() -> None:
    response = api_call('groups', params=[('o', 'MEMBERS')])
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_json_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups-with-members.json')

    validated: list[GroupInfo] = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.members is not None for x in validated)  # always set, even when empty
    assert any(x.members for x in validated)  # indirect validation: AccountInfo


def test_group_info_plus_includes() -> None:
    response = api_call('groups', params=[('o', 'INCLUDES')])
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_json_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups-with-includes.json')

    validated: list[GroupInfo] = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.includes is not None for x in validated)  # always set, even when empty
    assert any(x.includes for x in validated)  # at least one group must have subgroups


def test_group_audit_event_info() -> None:
    group_id = GROUP4.id
    response = api_call(f'groups/{group_id}/log.audit')
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    # TODO(amj): This file just keeps growing every time pytest is executed :/
    dump_json_to_file(parsed_response, TESTS_RESPONSE_DIR / 'group-audit-event-info.json')

    validated: list[GroupAuditEventInfo] = [GroupAuditEventInfo.model_validate(data) for data in parsed_response]

    # Make sure our picked group has all the things we want to test
    assert any(x.type == 'ADD_GROUP' for x in validated)  # the group adding is present in the results
    assert any(x.type == 'ADD_USER' for x in validated)  # at least one user was added
    assert any(x.type == 'REMOVE_USER' for x in validated)  # at least one user was removed

    # Now ensure the documentation is correct:
    # The group member that is added/removed. If type is ADD_USER or REMOVE_USER the member is
    # returned as detailed AccountInfo entity, if type is ADD_GROUP or REMOVE_GROUP the member is
    # returned as GroupInfo entity. Note that the name in GroupInfo will not be set if the member
    # group is not available.
    #
    # indirect validation: GroupInfo
    # indirect validation: AccountInfo
    assert all(isinstance(x.member, GroupInfo) for x in validated if x.type == 'ADD_GROUP')
    assert all(isinstance(x.member, AccountInfo) for x in validated if x.type == 'ADD_USER')
    assert all(isinstance(x.member, AccountInfo) for x in validated if x.type == 'REMOVE_USER')


# TODO(amj): test GroupInfo.more_groups=True
