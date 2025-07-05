from json import loads
from pathlib import Path
from pprint import pprint
from typing import Any

import requests

REPOSITORY_ROOT_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = REPOSITORY_ROOT_DIR / 'tests'
TESTS_RESPONSE_DIR = TESTS_DIR / 'responses'

GERRIT_HOST = 'localhost:8080'
GERRIT_URL = f'http://{GERRIT_HOST}/a'
GERRIT_RESPONSE_PREFIX = ")]}'"


class GerritAPIError(RuntimeError):
    """Custom exception for Gerrit API errors."""


def api_call(endpoint: str, method: str = 'GET', data: dict[str, Any] | None = None) -> requests.Response:
    url = f'{GERRIT_URL}/{endpoint}'
    headers = {'Accept': 'application/json'}
    response = requests.request(method, url, headers=headers, json=data, timeout=3)

    if not response.ok:
        raise GerritAPIError(response.status_code, response.text)

    return response


def parse_response_text(content: str) -> Any:  # noqa: ANN401
    return loads(content.removeprefix(GERRIT_RESPONSE_PREFIX))


def pretty_json(data: Any) -> None:  # noqa: ANN401
    pprint(data, indent=2, width=120)  # noqa: T203
