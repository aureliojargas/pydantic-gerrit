# Pydantic models for the Gerrit Projects endpoint
# https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html


from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit

from .changes import GitPersonInfo, WebLinkInfo


class TagInfo(BaseModelGerrit):
    """
    Contains information about a tag.

    https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#tag-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#get-tag
        {
            "ref": "refs/tags/v1.0",
            "revision": "49ce77fdcfd3398dc0dedbe016d1a425fd52d666",
            "object": "1624f5af8ae89148d1a3730df8c290413e3dcf30",
            "message": "Annotated tag",
            "tagger": {
                "name": "David Pursehouse",
                "email": "david.pursehouse@sonymobile.com",
                "date": "2014-10-06 07:35:03.000000000",
                "tz": 540
            }
        }
    """

    ref: str = Field(
        description='The ref of the tag.'
    )
    revision: str = Field(
        description='For lightweight tags, the revision of the commit to which the tag points. For annotated tags, the revision of the tag object.'
    )
    object: str | None = Field(
        default=None,
        description='The revision of the object to which the tag points. (only set for annotated tags)'
    )
    message: str | None = Field(
        default=None,
        description='The tag message. For signed tags, includes the signature. (only set for annotated tags)'
    )
    tagger: GitPersonInfo | None = Field(
        default=None,
        description='The tagger. (only set for annotated tags, if present in the tag)'
    )
    created: str | None = Field(
        default=None,
        description='The timestamp of when the tag was created. For annotated and signed tags, this is the timestamp of the tag object and is the same as the date field in the tagger. For lightweight tags, it is the commit timestamp of the commit to which the tag points, when the object is a commit. It is not set when the object is any other type.'
    )
    can_delete: bool | None = Field(
        default=None,
        description='Whether the calling user can delete this tag. (not set if false)'
    )
    web_links: list[WebLinkInfo] | None = Field(
        default=None,
        description='Links to the tag in external sites.'
    )
