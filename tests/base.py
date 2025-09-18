"""Base classes for testing Gerrit API entities."""

import json
from pathlib import Path
from typing import Any, Union, get_type_hints

import jsonschema
import pytest


class BaseEntityTest:
    """Base class with common test logic for all entity tests."""

    entity_name: str  # Override in subclasses, e.g., 'accounts', 'groups'
    version: str = "v3_12"  # Can be overridden for version-specific tests

    def get_test_cases(self):
        """Return list of test case names. Override if needed."""
        return ["basic", "with_details", "minimal"]

    @pytest.fixture
    def validator(self):
        """Override in implementation-specific base classes."""
        raise NotImplementedError


class SchemaTestBase(BaseEntityTest):
    """Base class for JSON Schema validation tests."""

    @pytest.fixture
    def schema(self):
        """Load the JSON schema for this entity."""
        schema_path = Path(f"schemas/{self.version}/{self.entity_name}.json")
        return json.loads(schema_path.read_text())

    @pytest.fixture
    def validator(self, schema):
        """Create a validator function for the schema."""
        return lambda data: jsonschema.validate(data, schema)

    def test_schema_structure(self, schema):
        """Verify the schema has the expected high-level structure."""
        assert "$schema" in schema
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_schema_properties(self, schema):
        """Verify all properties have proper type definitions."""
        for prop_name, prop_schema in schema["properties"].items():
            assert "type" in prop_schema or "$ref" in prop_schema

    def test_required_properties(self, schema):
        """Verify required field specifications."""
        if "required" in schema:
            assert isinstance(schema["required"], list)
            for field in schema["required"]:
                assert field in schema["properties"]


class PydanticTestBase(BaseEntityTest):
    """Base class for Pydantic model tests."""

    @pytest.fixture
    def model_class(self):
        """Get the Pydantic model class for this entity."""
        module = __import__(
            f"generated.pydantic.{self.version}.{self.entity_name}",
            fromlist=["*"]
        )
        return getattr(module, self.entity_name.title().replace("-", ""))

    @pytest.fixture
    def validator(self, model_class):
        """Create a validator function using the Pydantic model."""
        return model_class.model_validate

    def test_model_serialization(self, test_data_loader, model_class):
        """Test that models can serialize back to dict correctly."""
        data = test_data_loader(self.version, self.entity_name, "basic")
        model = model_class.model_validate(data)
        assert model.model_dump() == data


class DataclassTestBase(BaseEntityTest):
    """Base class for dataclass implementation tests."""

    @pytest.fixture
    def dataclass(self):
        """Get the dataclass for this entity."""
        module = __import__(
            f"generated.dataclass.{self.version}.{self.entity_name}",
            fromlist=["*"]
        )
        return getattr(module, self.entity_name.title().replace("-", ""))

    @pytest.fixture
    def validator(self, dataclass):
        """Create a validator function for the dataclass."""
        return lambda data: dataclass(**data)

    def test_dataclass_fields(self, dataclass, schema):
        """Verify dataclass fields match schema properties."""
        annotations = get_type_hints(dataclass)
        for prop_name in schema["properties"]:
            assert prop_name in annotations


def _is_optional(type_hint: Any) -> bool:
    """Check if a type hint is Optional."""
    origin = getattr(type_hint, "__origin__", None)
    args = getattr(type_hint, "__args__", ())
    return origin is Union and type(None) in args


class TypeddictTestBase(BaseEntityTest):
    """Base class for validating TypedDict generation."""

    @pytest.fixture
    def typeddict_class(self):
        """Get the TypedDict class for this entity."""
        module = __import__(
            f"generated.typeddict.{self.version}.{self.entity_name}",
            fromlist=["*"]
        )
        return getattr(module, self.entity_name.title().replace("-", ""))

    def _check_type_mapping(self, schema_type: str, td_type: Any) -> bool:
        """Verify type mapping between JSON Schema and TypedDict types."""
        if schema_type == "string":
            return td_type == str
        if schema_type == "number":
            return td_type in (float, int)
        if schema_type == "integer":
            return td_type == int
        if schema_type == "boolean":
            return td_type == bool
        if schema_type == "array":
            return getattr(td_type, "__origin__", None) == list
        if schema_type == "object":
            return True  # Could be dict or another TypedDict
        return False

    def test_fields_match_schema(self, typeddict_class, schema):
        """Verify the TypedDict has all fields from schema with correct types."""
        annotations = get_type_hints(typeddict_class)

        for prop_name, prop_schema in schema["properties"].items():
            assert prop_name in annotations

            if "type" in prop_schema:
                schema_type = prop_schema["type"]
                td_type = annotations[prop_name]

                # Handle Optional types
                if _is_optional(td_type):
                    td_type = td_type.__args__[0]

                assert self._check_type_mapping(schema_type, td_type)

    def test_required_fields(self, typeddict_class, schema):
        """Verify required fields are marked as required in TypedDict."""
        annotations = get_type_hints(typeddict_class)
        required_fields = schema.get("required", [])

        for field_name, field_type in annotations.items():
            if field_name in required_fields:
                assert not _is_optional(field_type)
            else:
                assert _is_optional(field_type)
