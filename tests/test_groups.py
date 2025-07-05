import json
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast

import pytest

from pydantic_gerrit.v3_12.groups import GroupInfo, GroupInput, GroupOptionsInfo, GroupOptionsInput, GroupsInput
from tests.helpers import TESTS_RESPONSE_DIR, GerritAPIError, api_call, parse_response_text

# These constants are set in setup_gerrit_groups_test()
GROUP1: GroupInfo
GROUP2: GroupInfo
GROUP3: GroupInfo
GROUP4: GroupInfo


def dump_to_file(data: Any, path: Path) -> None:  # noqa: ANN401
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def get_group(name: str) -> GroupInfo | None:
    """https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#get-group"""
    try:
        response = api_call(f'groups/{name}')
    except GerritAPIError as error:
        if error.args[0] == 404:  # noqa: PLR2004
            return None
        raise
    return GroupInfo.model_validate(parse_response_text(response.text))


def create_group(name: str, input_: GroupInput | None = None) -> GroupInfo:
    """https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#create-group"""

    if group := get_group(name):
        return group

    # direct validation: GroupInput
    data = input_.model_dump(mode='json') if input_ else {}
    response = api_call(f'groups/{name}', method='PUT', data=data)
    return GroupInfo.model_validate(parse_response_text(response.text))


def add_subgroups(parent_id: str, input_: GroupsInput | None = None) -> list[GroupInfo]:
    """https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#add-subgroups"""
    data = input_.model_dump(mode='json') if input_ else {}
    response = api_call(f'groups/{parent_id}/groups', method='POST', data=data)
    parsed_response: list[Any] = parse_response_text(response.text)
    return [GroupInfo.model_validate(x) for x in parsed_response]


# This raises "Deletion of Group is not enabled"
# Must edit `gerrit.config`, setting `gerrit.enableGroupDeletion` to true:
# git config -f /var/gerrit/etc/gerrit.config gerrit.enableGroupDeletion true
# /var/gerrit/bin/gerrit.sh restart
# but support for this was added in Nov 2024, so it won't work on older versions, we can't rely on that:
# 8463fb9c9d90dd8a8792cc861a84796528b893b1
def delete_group(id_: str) -> None:
    """https://gerrit-review.googlesource.com/Documentation/rest-api-groups.html#delete-group"""
    api_call(f'groups/{id_}', method='DELETE')


@pytest.fixture(scope='session')
def setup_gerrit_groups_test() -> Generator[str]:
    """Fixture to set up specific environment for group tests."""
    # Cannot delete groups on versions previous to Nov 2024, so any adding is permanent
    # https://gerrit-review.googlesource.com/c/gerrit/+/431917

    global GROUP1, GROUP2, GROUP3, GROUP4

    # Groups already available in a Gerrit fresh install
    GROUP1 = cast('GroupInfo', get_group(name='Administrators'))
    GROUP2 = cast('GroupInfo', get_group(name='Service Users'))
    GROUP3 = cast('GroupInfo', get_group(name='Blocked Users'))

    # My custom groups
    GROUP4 = create_group(
        name='test-group-4',
        input_=GroupInput(description='test-group-4 description', uuid='4' * 40, visible_to_all=False),
    )

    return  # This is where the tests in this file will be executed

    # Add your teardown code here. But you have to change from `return` to `yield`


# Apply the fixture automatically to all tests in this module
pytestmark = pytest.mark.usefixtures('setup_gerrit_groups_test')


def test_group_options() -> None:
    group_id = GROUP4.group_id
    input_ = GroupOptionsInput(visible_to_all=True)  # direct validation: GroupOptionsInput
    response = api_call(f'groups/{group_id}/options', method='PUT', data=input_.model_dump(mode='json'))
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_to_file(parsed_response, TESTS_RESPONSE_DIR / 'group-options.json')

    validated = GroupOptionsInfo.model_validate(parsed_response)
    assert validated.visible_to_all is True


def test_groups_input() -> None:  # direct validation: GroupsInput
    using_groups = add_subgroups(parent_id=GROUP4.id, input_=GroupsInput(groups=[GROUP1.id]))
    assert [x for x in using_groups if x.id == GROUP1.id]

    using_one_group = add_subgroups(parent_id=GROUP4.id, input_=GroupsInput(_one_group=GROUP2.id))
    assert [x for x in using_one_group if x.id == GROUP2.id]


def test_groups() -> None:
    response = api_call('groups')
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups.json')

    validated = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.options is not None for x in validated)  # always set, even when empty
    assert any(x.options for x in validated)  # indirect validation: GroupOptionsInfo
    assert all(x.members is None for x in validated)  # not set by default
    assert all(x.includes is None for x in validated)  # not set by default
    assert all(x.more_groups is None for x in validated)  # not set by default
    # not set if returned in a map where the group name is used as map key
    assert all(x.name is None for x in validated)


def test_groups_plus_members() -> None:
    response = api_call('groups?o=MEMBERS')
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups-with-members.json')

    validated = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.members is not None for x in validated)  # always set, even when empty
    assert any(x.members for x in validated)  # indirect validation: AccountInfo
    # TODO(amj): Instead of asserts, maybe have extra models such as GroupInfoPlusMembers


def test_groups_plus_includes() -> None:
    response = api_call('groups?o=INCLUDES')
    parsed_response: dict[str, Any] = parse_response_text(response.text)

    dump_to_file(parsed_response, TESTS_RESPONSE_DIR / 'groups-with-includes.json')

    validated = [GroupInfo.model_validate(data) for data in parsed_response.values()]
    assert all(x.includes is not None for x in validated)  # always set, even when empty
    assert any(x.includes for x in validated)  # at least one group must have subgroups
    # TODO(amj): Instead of asserts, maybe have extra models such as GroupInfoPlusIncludes


# TODO(amj): if doing extra models, the combination can be a nightmare. For example, GroupInfoPlusMembersAndIncludes
#            also, the models that use GroupInfo as as attribute type may also be affected by the `o=` options?

# TODO(amj): test GroupInfo.more_groups=True
