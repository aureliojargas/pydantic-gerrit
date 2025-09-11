from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit


class GitPersonInfo(BaseModelGerrit):
    """
    The GitPersonInfo entity contains information about the author/committer of a commit.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#git-person-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#get-tag (`tagger` field)
        {
            "name": "David Pursehouse",
            "email": "david.pursehouse@sonymobile.com",
            "date": "2014-10-06 07:35:03.000000000",
            "tz": 540
        }
    """

    name: str = Field(
        description='The name of the author/committer.',
    )
    email: str = Field(
        description='The email address of the author/committer.',
    )
    date: str = Field(
        # TODO(aj): Convert this to a datetime field?
        # https://gerrit-review.googlesource.com/Documentation/rest-api.html#timestamp
        description='The timestamp of when this identity was constructed. Timestamps are given in UTC and have the format "yyyy-mm-dd hh:mm:ss.fffffffff" where "fffffffff" represents nanoseconds.',
    )
    tz: int = Field(
        description='The timezone offset from UTC of when this identity was constructed.',
    )


class WebLinkInfo(BaseModelGerrit):
    """
    The WebLinkInfo entity describes a link to an external site.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#web-link-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#get-edit-meta-data
        {
            "name": "side-by-side preview diff",
            "image_url": "plugins/xdocs/static/sideBySideDiffPreview.png",
            "url": "#/x/xdocs/c/42/1..0/README.md",
        }
    """

    # TODO(aj): How about the `target` field that appears in the examples?

    name: str = Field(
        description='The text to be linkified.',
    )
    tooltip: str | None = Field(
        default=None,
        description='Tooltip to show when hovering over the link. Using "Open in $NAME_OF_EXTERNAL_TOOL" is a good option here.',
    )
    url: str = Field(
        description='The link URL.',
    )
    image_url: str | None = Field(
        default=None,
        description='URL to the icon of the link.',
    )
