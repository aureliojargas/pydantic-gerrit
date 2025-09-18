"""Pytest configuration and shared fixtures."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def test_data_loader() -> Callable[[str, str, str], dict[str, Any]]:
    """Create a loader function for test data files.

    Args:
        version: Gerrit version (e.g., 'v3_12')
        entity: Entity type (e.g., 'accounts', 'groups')
        case: Test case name (e.g., 'basic', 'with_details')

    Returns:
        Dict containing the loaded JSON data
    """

    def load_test_data(version: str, entity: str, case: str) -> dict[str, Any]:
        path = Path(__file__).parent / 'data' / version / entity / f'{case}.json'
        return json.loads(path.read_text())

    return load_test_data


@pytest.fixture
def schema_loader() -> Callable[[str, str], dict[str, Any]]:
    """Create a loader function for schema files.

    Args:
        version: Gerrit version (e.g., 'v3_12')
        entity: Entity type (e.g., 'accounts', 'groups')

    Returns:
        Dict containing the loaded JSON schema
    """

    def load_schema(version: str, entity: str) -> dict[str, Any]:
        path = Path('schemas') / version / f'{entity}.json'
        return json.loads(path.read_text())

    return load_schema
