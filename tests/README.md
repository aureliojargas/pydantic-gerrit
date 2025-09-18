# Testing Documentation

This directory contains the test suite for the Gerrit API type system. The tests are organized to validate multiple implementations of the same Gerrit entities using different Python type systems.

## Test Structure

- `base.py`: Contains base test classes that standardize testing across different implementations
- `conftest.py`: Pytest fixtures and utilities
- `data/`: Test data files organized by version and entity
- Entity-specific test files (e.g., `test_accounts.py`, `test_groups.py`)

## Testing Strategy

We validate four different implementations of each Gerrit entity:

1. JSON Schema (`SchemaTestBase`)
   - Validates schema structure and constraints
   - Tests type validations and required fields
   - Uses `jsonschema` library for validation

2. Pydantic Models (`PydanticTestBase`)
   - Tests model instantiation and validation
   - Validates nested object parsing
   - Ensures proper type coercion

3. Python Dataclasses (`DataclassTestBase`)
   - Tests dataclass instantiation
   - Validates nested object structure
   - Checks type annotations

4. TypedDict (`TypeddictTestBase`)
   - Tests static type hints
   - Validates structural typing
   - No runtime validation (static analysis only)

## Base Test Classes

The `BaseEntityTest` class provides common functionality:
- `entity_name`: Maps to the JSON schema file name
- `version`: Gerrit API version being tested (e.g., "v3_12")

Specialized base classes extend this for each implementation type:
- `SchemaTestBase`: JSON Schema validation
- `PydanticTestBase`: Pydantic model testing
- `DataclassTestBase`: Dataclass implementation testing
- `TypeddictTestBase`: TypedDict static typing tests

## Test Data

The project is organized into three main areas:

1. JSON Schemas (`schemas/v3_12/`)
   - Source of truth for entity definitions
   - One JSON schema file per entity

2. Generated Code (`generated/`)
   - Contains the three implementations (Pydantic, Dataclass, TypedDict)
   - Organized by implementation type and version
   - Generated from JSON schemas

3. Tests (`tests/`)
   - One test file per entity
   - Tests all implementations of each entity

Example structure:
```
generated/
    pydantic/
        v3_12/
            accounts.py
            groups.py
            ...
    dataclass/
        v3_12/
            accounts.py
            groups.py
            ...
    typeddict/
        v3_12/
            accounts.py
            groups.py
            ...
schemas/
    v3_12/
        accounts.json
        groups.json
        ...
tests/
    test_accounts.py
    test_groups.py
```

## Fixtures

Key fixtures in `conftest.py`:
- `test_data_loader`: Loads test data by version/entity/case
- `schema`: Provides JSON schema for current entity
- `model_class`: Provides Pydantic model class
- `dataclass`: Provides dataclass implementation
- `typeddict_class`: Provides TypedDict implementation

## Type Hints

We use Python 3.10+ type hint syntax:
- Use `dict[str, Any]` instead of `Dict[str, Any]`
- Use `Callable[[str, str, str], dict[str, Any]]` for test data loader
- Use `type[BaseModel]` for Pydantic model class references
- Explicit return type annotations with `-> None` for test methods

## Test Conventions

1. Test methods:
   - Clear, descriptive names indicating what's being tested
   - Docstrings explaining test purpose
   - One assertion concept per test method

2. Test data:
   - `basic`: Minimal valid data
   - `with_details`: Complete data with nested objects
   - `invalid`: Invalid data for testing constraints

3. Test coverage:
   - Schema structure and constraints
   - Data parsing and validation
   - Nested object handling
   - Type system specific features

## Running Tests

```bash
pytest tests/
```

To run specific test files:
```bash
pytest tests/test_accounts.py
pytest tests/test_groups.py
```

## Adding New Entity Tests

1. Generate implementation files in `generated/*/v3_12/`
2. Create test data files in `tests/data/v3_12/`
   - Create `basic.json` with minimal valid data
   - Create `with_details.json` with complete nested objects
   - Create `invalid.json` for testing constraints
3. Create new test file following existing patterns
4. Implement test classes for all four implementations
5. Follow type hint conventions
6. Ensure both `ruff format` and `ruff check` pass
