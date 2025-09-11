"""
Partial implementation for the `accounts` endpoint.

Only the models needed by the `groups` endpoint are implemented.
"""

from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit


class AccountInfo(BaseModelGerrit):
    """
    The AccountInfo entity contains information about an account.

    https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#account-info
    """

    account_id: int = Field(
        alias='_account_id',
        description='The numeric ID of the account.',
    )
    name: str | None = Field(
        default=None,
        description='The full name of the user. Only set if detailed account information is requested.',
    )
    display_name: str | None = Field(
        default=None,
        description='The display name of the user. Only set if detailed account information is requested.',
    )
    email: str | None = Field(
        default=None,
        description='The email address the user prefers to be contacted through. Only set if detailed account information is requested.',
    )
    secondary_emails: list[str] | None = Field(
        default=None,
        description='A list of the secondary email addresses of the user. Only set for account queries when the ALL_EMAILS option or the suggest parameter is set. Secondary emails are only included if the calling user has the Modify Account, and hence is allowed to see secondary emails of other users.',
    )
    username: str | None = Field(
        default=None,
        description='The username of the user. Only set if detailed account information is requested.',
    )
    avatars: list['AvatarInfo'] | None = Field(
        default=None,
        description='List of AvatarInfo entities that provide information about avatar images of the account.',
    )
    more_accounts: bool | None = Field(
        default=None,
        alias='_more_accounts',
        description='Whether the query would deliver more results if not limited. Only set on the last account that is returned. (not set if false)',
    )
    status: str | None = Field(
        default=None,
        description='Status message of the account.',
    )
    inactive: bool | None = Field(
        default=None,
        description='Whether the account is inactive. (not set if false)',
    )
    tags: list[str] | None = Field(
        default=None,
        description='List of additional tags that this account has. The only current tag an account can have is SERVICE_USER. Only set if detailed account information is requested. (not set if empty)',
    )


class AvatarInfo(BaseModelGerrit):
    """
    The AvatarInfo entity contains information about an avatar image of an account.

    https://gerrit-review.googlesource.com/Documentation/rest-api-accounts.html#avatar-info
    """

    url: str = Field(
        description='The URL to the avatar image.',
    )
    height: int = Field(
        description='The height of the avatar image in pixels.',
    )
