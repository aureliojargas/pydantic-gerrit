from pydantic_gerrit.v3_12.accounts import AccountInfo
from tests.helpers import GerritAPIError, api_call, parse_response_text


def get_account(account_id: str) -> AccountInfo | None:
    """https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#get-account"""
    try:
        response = api_call(f'accounts/{account_id}')
    except GerritAPIError as error:
        if error.args[0] == 404:  # noqa: PLR2004
            return None
        raise
    return AccountInfo.model_validate(parse_response_text(response.text))
