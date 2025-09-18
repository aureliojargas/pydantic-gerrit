"""Test module for the Gerrit groups entity."""

from collections.abc import Callable
from typing import Any, get_type_hints

import jsonschema
import pytest
from pydantic import BaseModel

from .base import (
    DataclassTestBase,
    PydanticTestBase,
    SchemaTestBase,
    TypeddictTestBase,
)


class GroupSchemaTests(SchemaTestBase):
    """Test the Group JSON Schema."""

    entity_name = 'groups'

    def test_group_id_type(
        self, schema: dict[str, Any], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that group_id must be an integer."""
        # Valid group_id should pass
        valid_data = test_data_loader(self.version, self.entity_name, 'basic')
        jsonschema.validate(valid_data, schema)

        # Invalid group_id should fail
        invalid_data = test_data_loader(self.version, self.entity_name, 'invalid')
        with pytest.raises(jsonschema.exceptions.ValidationError, match="is not of type 'integer'"):
            jsonschema.validate(invalid_data, schema)

    def test_members_schema(self, schema: dict[str, Any]) -> None:
        """Test that members field has correct schema."""
        members_schema = schema['properties']['members']
        assert members_schema['type'] == 'array'
        assert '$ref' in members_schema['items']


class GroupPydanticTests(PydanticTestBase):
    """Test the Group Pydantic model."""

    entity_name = 'groups'

    def test_members_parsing(
        self, model_class: type[BaseModel], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that member accounts are properly parsed."""
        data = test_data_loader(self.version, self.entity_name, 'with_details')
        group = model_class.model_validate(data)
        assert len(group.members) == 2
        assert group.members[0].username == 'jdoe'

    def test_includes_parsing(
        self, model_class: type[BaseModel], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that included groups are properly parsed."""
        data = test_data_loader(self.version, self.entity_name, 'with_details')
        group = model_class.model_validate(data)
        assert len(group.includes) == 1
        assert group.includes[0].name == 'Contributors'


class GroupDataclassTests(DataclassTestBase):
    """Test the Group dataclass implementation."""

    entity_name = 'groups'

    def test_nested_dataclasses(
        self, dataclass: type, test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that nested objects are properly converted to dataclasses."""
        data = test_data_loader(self.version, self.entity_name, 'with_details')
        group = dataclass(**data)
        assert isinstance(group.options, dict)  # or specific Options class
        assert isinstance(group.members, list)


class GroupTypeddictTests(TypeddictTestBase):
    """Test the Group TypedDict implementation."""

    entity_name = 'groups'

    def test_nested_types(self, typeddict_class: type) -> None:
        """Test nested type definitions."""
        # Note: This is just structural validation
        type_hints = get_type_hints(typeddict_class)
        assert 'members' in type_hints
        assert 'includes' in type_hints
