"""Tests for Account entity implementations."""

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


class AccountSchemaTests(SchemaTestBase):
    """Test the Account JSON Schema."""

    entity_name = 'accounts'

    def test_email_format(
        self, schema: dict[str, Any], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that email validation works."""
        # Valid email should pass
        valid_data = test_data_loader(self.version, self.entity_name, 'basic')
        jsonschema.validate(valid_data, schema)

        # Invalid email should fail
        invalid_data = test_data_loader(self.version, self.entity_name, 'invalid_email')
        with pytest.raises(jsonschema.exceptions.ValidationError, match="is not a 'email'"):
            jsonschema.validate(invalid_data, schema)

    def test_registered_on_format(
        self, schema: dict[str, Any], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that registered_on date format is validated."""
        data = test_data_loader(self.version, self.entity_name, 'basic')
        jsonschema.validate(data, schema)


class AccountPydanticTests(PydanticTestBase):
    """Test the Account Pydantic model."""

    entity_name = 'accounts'

    def test_email_validation(
        self, model_class: type[BaseModel], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that email validation works in Pydantic model."""
        # Valid email should pass
        valid_data = test_data_loader(self.version, self.entity_name, 'basic')
        account = model_class.model_validate(valid_data)
        assert account.email == valid_data['email']

        # Invalid email should fail
        invalid_data = test_data_loader(self.version, self.entity_name, 'invalid_email')
        with pytest.raises(ValueError, match='value is not a valid email address'):
            model_class.model_validate(invalid_data)

    def test_optional_fields(
        self, model_class: type[BaseModel], test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test that optional fields are handled correctly."""
        minimal_data = test_data_loader(self.version, self.entity_name, 'minimal')
        account = model_class.model_validate(minimal_data)
        assert account.email is None
        assert account.username is None


class AccountDataclassTests(DataclassTestBase):
    """Test the Account dataclass implementation."""

    entity_name = 'accounts'

    def test_field_types(self, dataclass: type, test_data_loader: Callable[[str, str, str], dict[str, Any]]) -> None:
        """Test that field types are correct."""
        data = test_data_loader(self.version, self.entity_name, 'with_details')
        account = dataclass(**data)
        assert isinstance(account.name, str)
        assert isinstance(account.tags, list)
        assert isinstance(account._number, int)


class AccountTypeddictTests(TypeddictTestBase):
    """Test the Account TypedDict implementation."""

    entity_name = 'accounts'

    def test_complete_structure(
        self, typeddict_class: type, test_data_loader: Callable[[str, str, str], dict[str, Any]]
    ) -> None:
        """Test complete account structure matches TypedDict."""
        data = test_data_loader(self.version, self.entity_name, 'with_details')
        # Note: This is just structural validation, no runtime type checking
        type_hints = get_type_hints(typeddict_class)
        assert all(field in type_hints for field in data)
